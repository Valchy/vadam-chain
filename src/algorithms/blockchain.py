import copy
import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass
import time

from ipv8.community import CommunitySettings
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from ipv8.types import Peer

from da_types import Blockchain, message_wrapper
from merkle_util import merkle_root, merkle_proof

# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)


@dataclass(
    msg_id=1
)
class Transaction:
    sender: int
    receiver: int
    amount: int
    public_key_bin: bytes
    signature: bytes
    nonce: int = 1

    def __post_init__(self):
        self.tx_id = hashlib.sha256(f'{self.sender}{self.receiver}{self.amount}{self.nonce}'.encode()).hexdigest()

@dataclass(
    msg_id=2
)
class Block:
    def __init__(self, number, prev_block_time, prev_block_hash, difficulty, target):
        self.transactions:list[Transaction] = []
        self.number = number
        self.hash = 0
        self.timestamp = 0
        self.prev_block_hash = prev_block_hash
        self.difficulty = difficulty
        self.target = target
        self.nonce = 0
        self.hashing_value = ""

    def get_hashing_value(self):
        return "".join([tx.tx_id for tx in self.transactions]).join(str(self.nonce))
        

    def add_transaction(self, transaction: Transaction):
        if len(self.transactions) < 10:
            self.transactions.append(transaction)
        else:
            pass

    def mine(self):
        while True:
            self.hashing_value = self.get_hashing_value()
            self.hash = hashlib.sha256(self.hashing_value.encode()).hexdigest()
            if int(self.hash, 16) < self.target:
                return self.hash
            self.nonce += 1
        



    # def verify_transaction(self, transaction):
    #     return merkle_proof(transaction.tx_id, [tx.tx_id for tx in self.transactions])




class BlockchainNode(Blockchain):

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.counter = 1
        self.max_messages = 5
        self.executed_checks = 0

        self.pending_txs = []
        self.finalized_txs = []
        self.balances = defaultdict(lambda: 1000)
        self.blocks: list[Block] = []

        self.difficulty = 115763819684279741274297652248676021157016744923290554136127638308692447723520
        self.target_block_time = 10
        self.puzzle_target = self.calculate_puzzle_target()
        self.curr_block = Block(number=0, prev_block_time=time.time(), prev_block_hash='0', difficulty=self.difficulty, target=self.puzzle_target)

        #add structure to storing transactions in blocks
        self.key_pair = self.crypto.generate_key("medium")
        self.add_message_handler(Transaction, self.on_transaction)


    def create_block(self):
        self.calculate_difficulty()
        self.calculate_puzzle_target()
        self.curr_block = Block(prev_block_hash=self.blocks[-1].hash,
                                prev_block_time=self.blocks[-1].time,
                                difficulty= self.difficulty,
                                target=self.puzzle_target,
                                number=self.blocks[-1].number + 1)


    def calculate_difficulty(self):
        avg_block_time = 0
        if len(self.blocks) < 100:
            avg_block_time = (self.blocks[-1].timestamp - self.blocks[0].timestamp) / len(self.blocks)
        else:
            avg_block_time = (self.blocks[-1].timestamp - self.blocks[-100].timestamp) / 100
        self.difficulty = self.difficulty * self.target_block_time / avg_block_time

    def calculate_puzzle_target(self):
        max_value = hex(0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff)
        return max_value - self.difficulty


    def sign_transaction(self, transaction: Transaction) -> None:
        transaction.signature = self.crypto.create_signature(self.my_peer.key,
                                                             self.serializer.pack_serializable(transaction))

    def verify_signature(self, transaction: Transaction) -> bool:

        # create transaction copy without signature and then verify
        tx_copy = copy.deepcopy(transaction)
        tx_copy.signature = b''
        public_key = self.crypto.key_from_public_bin(tx_copy.public_key_bin)
        return self.crypto.is_valid_signature(public_key,
                                              self.serializer.pack_serializable(tx_copy),
                                              transaction.signature)

    def create_transaction(self):
        peer = random.choice([i for i in self.get_peers() if self.node_id_from_peer(i) % 2 == 1])
        peer_id = self.node_id_from_peer(peer)
        tx = Transaction(self.node_id, peer_id, 10, b'', b'', self.counter)
        tx.public_key_bin = self.my_peer.public_key.key_to_bin()
        self.sign_transaction(tx)
        self.counter += 1
        print(f'[Node {self.node_id}] Sending transaction {tx.nonce} to {self.node_id_from_peer(peer)}')
        self.ez_send(peer, tx)

        if self.counter > self.max_messages:
            self.cancel_pending_task("tx_create")
            self.stop()
            return

    def process_pending_transactions(self):
        if len(self.pending_txs) < 10:
            for txs in self.pending_txs:
                self.curr_block.add_transaction(txs)
        else:
            for i in range(10):
                self.curr_block.add_transaction(self.pending_txs[i])

    def on_start(self):
        if self.node_id % 2 == 0:
            #  Run client
            self.start_client()
        else:
            # Run validator
            self.start_validator()

    def start_client(self):
        # Create transaction and send to random validator
        # Or put node_id
        self.register_task("tx_create",
                           self.create_transaction, delay=1,
                           interval=1)

    def start_validator(self):
        self.register_task("check_txs", self.check_transactions, delay=2, interval=1)

    def check_transactions(self):
        for tx in self.pending_txs:
            # block = self.find_block_for_transaction(tx)
            if self.balances[tx.sender] - tx.amount >= 0:
                self.balances[tx.sender] -= tx.amount
                self.balances[tx.receiver] += tx.amount
                self.pending_txs.remove(tx)
                self.finalized_txs.append(tx)

        self.executed_checks += 1

        if self.executed_checks > 10:
            self.cancel_pending_task("check_txs")
            print(self.balances)
            self.stop()

    def verify_block(self, block: Block) -> bool:
        # Verify block hash
        return block.hash == block.mine()

    @message_wrapper(Transaction)
    async def on_transaction(self, peer: Peer, payload: Transaction) -> None:
        if self.verify_signature(payload):
            # Add to pending transactions if signature is verified
            print(f'[Node {self.node_id}] Received transaction {payload.nonce} from {self.node_id_from_peer(peer)}')
            if (payload.sender, payload.nonce) not in [(tx.sender, tx.nonce) for tx in self.finalized_txs] and (
                    payload.sender, payload.nonce) not in [(tx.sender, tx.nonce) for tx in self.pending_txs]:
                self.pending_txs.append(payload)
                self.process_pending_transactions()
        else:

            # Gossip to other nodes
            for peer in [i for i in self.get_peers() if self.node_id_from_peer(i) % 2 == 1]:
                self.ez_send(peer, payload)
    
    @message_wrapper(Block)
    async def on_block(self, peer: Peer, payload: Block) -> None:
        if self.verify_block(payload):
            print(f'[Node {self.node_id}] Received block {payload.number} from {self.node_id_from_peer(peer)}')
            self.blocks.append(payload)
            self.create_block()
        else:
            for peer in [i for i in self.get_peers() if self.node_id_from_peer(i) % 2 == 0]:
                self.ez_send(peer, payload)
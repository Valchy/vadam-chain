import copy
import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass
import time
import asyncio

from ipv8.community import CommunitySettings
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from ipv8.types import Peer

from src.da_types import Blockchain, message_wrapper
from src.merkle_util import merkle_root, merkle_proof
from src.log.logging_config import *

setup_logging()

# Create logger
logger = logging.getLogger('my_app')

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
    ttl: int = 3

    def __post_init__(self):
        self.tx_id = hashlib.sha256(f'{self.sender}{self.receiver}{self.amount}{self.nonce}'.encode()).hexdigest()


@dataclass(
    msg_id=2
)
class Block:
    number: int
    prev_block_time: int
    prev_block_hash: str
    difficulty: int
    puzzle_target: int
    transactions: list[Transaction]

    def __post_init__(self):
        self.hash = 0
        self.timestamp = 0
        self.nonce = 0
        self.hashing_value = ""

    def get_hashing_value(self):
        return "".join([tx.tx_id for tx in self.transactions]).join(str(self.nonce))

    def add_transaction(self, transaction: Transaction) -> bool:
        if len(self.transactions) < 10:
            self.transactions.append(transaction)
            return True
        else:
            return False

    async def mine(self):
        now = time.time()
        loop = asyncio.get_event_loop()
        while True:
            self.hashing_value = self.get_hashing_value()
            self.hash = await loop.run_in_executor(None, hashlib.sha256, self.hashing_value.encode())
            self.hash = self.hash.hexdigest()
            if int(self.hash, 16) < self.target:
                self.timestamp = int(self.prev_block_time + time.time() - now)
                return self.hash
            self.nonce += 1




@dataclass(
    msg_id=3
)
class BlocksRequest:
    sender: int
    start_block_number: int
    end_block_number: int

    def __post_init__(self):
        self.tx_id = hashlib.sha256(f'{self.sender}{self.start_block_number}{self.end_block_number}'.encode()).hexdigest()

class BlockchainNode(Blockchain):

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.counter = 1
        self.max_messages = 5
        self.executed_checks = 0

        self.pending_txs: list[Transaction] = []
        self.finalized_txs: list[Transaction] = []
        self.balances = defaultdict(lambda: 1000)
        self.blocks: list[Block] = []

        self.difficulty:int = 115763819684279741274297652248676021157016744923290554136127638308692447723520
        self.target_block_time = 10
        self.puzzle_target = self.calculate_puzzle_target()
        self.curr_block = Block(0, time.time(), '0', self.difficulty, self.puzzle_target, [])

        self.key_pair = self.crypto.generate_key("medium")
        self.add_message_handler(Transaction, self.on_transaction)
        self.add_message_handler(Block, self.on_block)
        self.add_message_handler(BlocksRequest, self.on_blocks_request)

    def create_block(self):
        self.calculate_difficulty()
        self.calculate_puzzle_target()
        self.curr_block = Block(prev_block_hash=self.blocks[-1].hash,
                                prev_block_time=self.blocks[-1].timestamp,
                                difficulty=self.difficulty,
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
        max_value = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return max_value - self.difficulty

    def sign_transaction(self, transaction: Transaction) -> None:
        transaction.signature = self.crypto.create_signature(self.my_peer.key,
                                                             self.serializer.pack_serializable(transaction))

    def verify_signature(self, transaction: Transaction) -> bool:

        tx_copy = copy.deepcopy(transaction)
        tx_copy.signature = b''
        # rm ttl before validation
        public_key = self.crypto.key_from_public_bin(tx_copy.public_key_bin)
        return self.crypto.is_valid_signature(public_key,
                                              self.serializer.pack_serializable(tx_copy),
                                              transaction.signature)

    def create_transaction(self, peer):
        peer_id = self.node_id_from_peer(peer)
        tx = Transaction(self.node_id, peer_id, 10, b'', b'', self.counter)
        tx.public_key_bin = self.my_peer.public_key.key_to_bin()
        # remove ttl before signing
        self.sign_transaction(tx)
        # add ttl
        self.counter += 1
        return tx

    def send_transaction(self, peer):
        tx = self.create_transaction(peer)

        logger.info(f'[Node {self.node_id}] Sending transaction {tx.nonce} to [Node {self.node_id_from_peer(peer)}]')
        logger.info(f'[Node {self.node_id}] Sending transaction {tx.nonce} to [Node {self.node_id_from_peer(peer)}]')
        self.ez_send(peer, tx)

        # ?
        if self.counter > self.max_messages:
            self.cancel_pending_task("tx_create")
            self.stop()
            return

    def process_pending_transactions(self):
        for txs in self.pending_txs:
            result = self.curr_block.add_transaction(txs)
            if result == False:
                return

    def on_start(self):
        if self.node_id == 0:
            self.start_client()
        else:
            self.start_validator()

    def start_client(self):
        first_peer = random.choice([i for i in self.get_peers()])
        self.register_task("tx_create",
                           self.send_transaction(first_peer), delay=1,
                           interval=1)

    def start_validator(self):
        self.register_task("check_txs", self.check_transactions, delay=2, interval=1)

    def check_transactions(self):
        for tx in self.pending_txs:
            if self.balances[tx.sender] - tx.amount >= 0:
                self.balances[tx.sender] -= tx.amount
                self.balances[tx.receiver] += tx.amount
                self.pending_txs.remove(tx)
                self.finalized_txs.append(tx)

        self.executed_checks += 1

        if self.executed_checks > 10:
            self.cancel_pending_task("check_txs")
            print(self.balances)
            logger.info(self.balances)
            print(f'amount of transactions: {len(self.curr_block.transactions)}')
            logger.info(f'amount of transactions: {len(self.curr_block.transactions)}')
            self.stop()

    def verify_block(self, block: Block) -> bool:
        if block.hash != hashlib.sha256(block.get_hashing_value().encode()).hexdigest()\
        and int(block.hash, 16) < self.target:
            return False
        else:
            return True

    @message_wrapper(Transaction)
    async def on_transaction(self, peer: Peer, payload: Transaction) -> None:
        if self.verify_signature(payload):
            print(f'transaction nonce:{payload.nonce}')
            logger.info(f'transaction nonce:{payload.nonce}')
            print(f'[Node {self.node_id}] Received transaction {payload.nonce} from [Node {self.node_id_from_peer(peer)}]')
            logger.info(f'[Node {self.node_id}] Received transaction {payload.nonce} from [Node {self.node_id_from_peer(peer)}]')

            if (payload.sender, payload.nonce) not in [(tx.sender, tx.nonce) for tx in self.finalized_txs] and (
                    payload.sender, payload.nonce) not in [(tx.sender, tx.nonce) for tx in self.pending_txs]:

                self.pending_txs.append(payload)
                self.process_pending_transactions()

                if payload.ttl > 0:
                    payload.ttl -= 1

                    # we send here to all neighbours
                    for peer in self.get_peers():
                        print(f'[Node {self.node_id}] Send transaction {payload.nonce} to [Node {self.node_id_from_peer(peer)}]')
                        logger.info(f'[Node {self.node_id}] Send transaction {payload.nonce} to [Node {self.node_id_from_peer(peer)}]')
                        self.ez_send(peer, payload)
                else:
                    pass
        else:
            pass

    def create_blocks_request(self, sender, start_block_number, end_block_number):
        request = BlocksRequest(sender, start_block_number, end_block_number)
        return request

    def clean_pending_txs(self, block):
        # we need to remove from pending_txs transactions that were already included in mined block
        cleaned_pending_txs = []
        for tx in self.pending_txs:
            if tx not in block.transactions:
                cleaned_pending_txs.append(tx)
        self.pending_txs = cleaned_pending_txs

    @message_wrapper(Block)
    async def on_block(self, peer: Peer, payload: Block) -> None:
        if self.verify_block(payload):
            print(f'[Node {self.node_id}] Received block {payload.number} from [Node {self.node_id_from_peer(peer)}]')
            logger.info(f'[Node {self.node_id}] Received block {payload.number} from [Node {self.node_id_from_peer(peer)}]')

            # pull gossip
            if (payload.number - self.blocks[-1].number) == 1:
                # we received block  that we can append
                self.blocks.append(payload)
                self.clean_pending_txs(payload)

                # ?
                self.create_block()

                # broadcast to all peers
                for peer in self.get_peers():
                    self.ez_send(peer, payload)
            elif (payload.number - self.blocks[-1].number) < 1:
                # we already have this block, then
                # broadcast to all peers
                for peer in self.get_peers():
                    self.ez_send(peer, payload)
            else:
                # we received block that we don't have
                # and it cannot be appended
                start_block_number = self.blocks[-1].number+1
                end_block_number = payload.number
                request_message = self.create_block_request(self.node_id, start_block_number, end_block_number)
                for peer in self.get_peers():
                    self.ez_send(peer, request_message)

    @message_wrapper(BlocksRequest)
    async def on_blocks_request(self, peer: Peer, payload: BlocksRequest) -> None:
        last_possible_block_number = min(payload.end_block_number+1, self.blocks[-1].number)
        for i in range(payload.start_block_number, last_possible_block_number):
            self.ez_send(payload.sender, self.blocks[i])
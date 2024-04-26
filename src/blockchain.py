import copy
import hashlib
import random
from binascii import hexlify
from collections import defaultdict
from dataclasses import dataclass
import time
from decimal import Decimal

from ipv8.community import CommunitySettings
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from ipv8.types import Peer

from algorithms.echo_algorithm import *
from algorithms.ring_election import *

from da_types import Blockchain, message_wrapper
from merkle_util import merkle_root, merkle_proof
from log.logging_config import *


# Create logger
# setup_logging()
#
#
# logger = logging.getLogger('my_app')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='./log/app.log',)
# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)

@dataclass(
    msg_id=1
)
class Transaction:
    sender: int
    receiver: int
    is_uniswap = False
    coin = "ETH"
    amount: int
    public_key_bin: bytes
    signature: bytes
    tx_id: str
    nonce: int
    ttl: int = 3

    # def __post_init__(self):
    #     self.tx_id = hashlib.sha256(f'{self.sender}{self.receiver}{self.amount}{self.nonce}'.encode()).hexdigest()


@dataclass(
    msg_id=2
)
class Block:
    number: int
    prev_block_time: int
    prev_block_hash: str
    difficulty: str
    puzzle_target: str
    transactions: list[Transaction]
    time: int
    hash: str
    nonce: int

    def __post_init__(self):
        # self.hash = 0
        # self.time = 0
        # self.nonce = 0
        self.hashing_value = ""

    def get_hashing_value(self, public_key_bin):
        # fix bug: 'Transaction' object has no attribute 'tx_id'
        return "".join([tx.tx_id for tx in self.transactions]) + str(self.nonce) + str(self.number) + str(public_key_bin)

    def add_transaction(self, transaction: Transaction) -> bool:
        if len(self.transactions) < 10:
            if transaction not in self.transactions:
                self.transactions.append(transaction)
            return True
        else:
            return False

    # def mine(self):
    #     now = time.time()
    #     loop = asyncio.get_event_loop()
    #     logger.info(f'Someone is mining block {self.number}...')
    #     while True:
    #         self.hashing_value = self.get_hashing_value()
    #         self.hash = hashlib.sha256(self.hashing_value.encode()).hexdigest()
    #         # Use 2^target for comparison
    #         target_value = 2 ** Decimal(self.puzzle_target)
    #
    #         if int(self.hash, 16) < target_value:
    #             self.time = int(self.prev_block_time + time.time() - now)
    #             logger.info(f'Block {self.number} is mined. Here is hash: {self.hash}')
    #             logger.info(f'Block {self.number} based on hashing value:{self.hashing_value}')
    #             logger.info(f'Block {self.number} based on nonce:{self.nonce}')
    #             logger.info(f'It took {time.time() - now} seconds to mine this block {self.number}')
    #             return self.hash
    #         self.nonce += 1



@dataclass(
    msg_id=3
)
class BlocksRequest:
    sender: int
    start_block_number: int
    end_block_number: int

    def __post_init__(self):
        self.tx_id = hashlib.sha256(
            f'{self.sender}{self.start_block_number}{self.end_block_number}'.encode()).hexdigest()


# class LiquidityPool:
#     def __init__(self):
#         self.pools = {'BTC': 10000, 'ETH': 100000}
#         self.c = self.pools["BTC"] * self.pools["ETH"]
#
#     def add_liquidity(self, btc_amount, eth_amount):
#         self.pools['BTC'] += btc_amount
#         self.pools['ETH'] += eth_amount
#         print(f"Added liquidity: {btc_amount} BTC and {eth_amount} ETH")
#
#     def remove_liquidity(self, btc_amount, eth_amount):
#         if self.pools['BTC'] >= btc_amount and self.pools['ETH'] >= eth_amount:
#             self.pools['BTC'] -= btc_amount
#             self.pools['ETH'] -= eth_amount
#             print(f"Removed liquidity: {btc_amount} BTC and {eth_amount} ETH")
#         else:
#             print("Insufficient liquidity to remove.")


# @dataclass(
#     msg_id=4
# )
# class UniswapTransactions:
#     def __init__(self, node):
#         self.node = node
#
#     def swap(self, from_coin, to_coin, amount):
#         if self.node.get_balance(from_coin) >= amount:
#             self.node.update_balance(from_coin, -amount)
#             self.node.update_balance(to_coin, amount * to_coin/from_coin)
#             print(f"Swapped {amount} {from_coin} for {amount} {to_coin}")
#         else:
#             print(f"Not enough {from_coin} to perform the swap.")
#
#     def add_liquidity(self, btc_amount, eth_amount):
#         if self.node.get_balance('BTC') >= btc_amount and self.node.get_balance('ETH') >= eth_amount:
#             self.node.update_balance('BTC', -btc_amount)
#             self.node.update_balance('ETH', -eth_amount)
#             self.node.liquidity_pool.add_liquidity(btc_amount, eth_amount)
#         else:
#             print("Insufficient balance to add liquidity.")
#
#     def exit_liquidity(self, btc_amount, eth_amount):
#         if self.node.liquidity_pool.pools['BTC'] >= btc_amount and self.node.liquidity_pool.pools['ETH'] >= eth_amount:
#             self.node.update_balance('BTC', btc_amount)
#             self.node.update_balance('ETH', eth_amount)
#             self.node.liquidity_pool.remove_liquidity(btc_amount, eth_amount)
#         else:
#             print("Insufficient liquidity to exit.")


class BlockchainNode(Blockchain):
    def __init__(self, settings: CommunitySettings) -> None:
        self.logger = logging.getLogger(__name__)

        super().__init__(settings)
        self.counter = 1
        self.max_messages = 15
        self.executed_checks = 0

        self.pending_txs: list[Transaction] = []
        self.finalized_txs: list[Transaction] = []
        self.balances = defaultdict(lambda:  {'BTC': 100, 'ETH': 1000})
        self.pools = {'BTC': 10000, 'ETH': 100000}
        self.c = self.pools["BTC"] * self.pools["ETH"]
        self.blocks: list[Block] = []
        self.longest_chain: list[Block] = []
        self.collision_num: int = 0

        self.difficulty: str = "13"
        self.target_block_time = 3
        self.puzzle_target = self.calculate_puzzle_target()
        self.curr_block = self.create_current_block()
        # Block(1, int(time.time()), '0', str(self.difficulty), str(self.puzzle_target), [],  int(time.time()), '0')

        # add structure to storing transactions in blocks
        self.key_pair = self.crypto.generate_key("medium")
        self.add_message_handler(Transaction, self.on_transaction)
        self.add_message_handler(Block, self.on_block)
        self.add_message_handler(BlocksRequest, self.on_blocks_request)

    def add_liquidity(self, btc_amount, eth_amount):
        self.pools['BTC'] += btc_amount
        self.pools['ETH'] += eth_amount
        self.balances['BTC'] -= btc_amount
        self.balances['ETH'] -= eth_amount
        print(f"Added liquidity: {btc_amount} BTC and {eth_amount} ETH")

    def remove_liquidity(self, btc_amount, eth_amount):
        if self.pools['BTC'] >= btc_amount and self.pools['ETH'] >= eth_amount:
            self.pools['BTC'] -= btc_amount
            self.pools['ETH'] -= eth_amount
            self.balances['BTC'] += btc_amount
            self.balances['ETH'] += eth_amount
            print(f"Removed liquidity: {btc_amount} BTC and {eth_amount} ETH")
        else:
            print("Insufficient liquidity to remove.")

    def create_block(self):
        self.calculate_difficulty()
        self.calculate_puzzle_target()
        self.curr_block = Block(prev_block_hash=self.blocks[-1].hash,
                                prev_block_time=self.blocks[-1].time,
                                difficulty=str(self.difficulty),
                                puzzle_target=self.puzzle_target,
                                transactions=[],
                                number=self.blocks[-1].number + 1,
                                time=int(time.time()),
                                hash='0',
                                nonce=0)

    def create_current_block(self):
        try:
            self.calculate_difficulty()
            self.calculate_puzzle_target()
        except:
            pass
        return Block(1, int(time.time()), '0', self.difficulty, self.puzzle_target, [], int(time.time()), '0',
                     0)

    def calculate_difficulty(self):
        if len(self.blocks) > 1:
            avg_block_time = (self.blocks[-1].time - self.blocks[0].time) / len(self.blocks)
        else:
            avg_block_time = self.target_block_time  # Fallback to target block time if not enough blocks

        # Calculate difficulty as base-2 logarithm
        current_difficulty_log = Decimal(self.difficulty)
        if avg_block_time < self.target_block_time:
            new_difficulty_log = current_difficulty_log + Decimal('0.13750352375')  # Approximation for log2(1.1)
        else:
            new_difficulty_log = current_difficulty_log - Decimal('0.13750352375')  # Approximation for log2(0.9)

        # Convert the new difficulty back to string for consistency with existing code
        self.difficulty = str(new_difficulty_log)
        print(f'Node {self.node_id} difficulty log2: {new_difficulty_log}')


    def calculate_puzzle_target(self):
        # Max value in log scale
        max_value_log = Decimal(256)  # Equivalent to log2(2^256)

        # Calculate target as difference from max value
        current_difficulty_log = Decimal(self.difficulty)
        new_puzzle_target_log = max_value_log - current_difficulty_log

        # Store and return the puzzle target in log scale
        self.puzzle_target = str(new_puzzle_target_log)
        try:
            print(f'Node {self.node_id} puzzle target log2: {new_puzzle_target_log}')
        except:
            pass
        return self.puzzle_target

    def sign_transaction(self, transaction: Transaction) -> None:
        initial_ttl = transaction.ttl
        transaction.ttl = 0
        transaction.signature = self.crypto.create_signature(self.my_peer.key, self.serializer.pack_serializable(transaction))
        transaction.ttl = initial_ttl

    def verify_signature(self, transaction: Transaction) -> bool:
        # create transaction copy without signature and then verify
        tx_copy = copy.deepcopy(transaction)
        tx_copy.signature = b''
        tx_copy.ttl = 0
        public_key = self.crypto.key_from_public_bin(tx_copy.public_key_bin)
        return self.crypto.is_valid_signature(public_key, self.serializer.pack_serializable(tx_copy), transaction.signature)

    def create_transaction(self):
        peer = random.choice([i for i in self.get_peers()])
        peer_id = self.node_id_from_peer(peer)
        tx = Transaction(self.node_id, peer_id, 10, b'', b'', '', self.counter)
        tx.public_key_bin = self.my_peer.public_key.key_to_bin()
        # tx.tx_id = hashlib.sha256(f'{tx.sender}{tx.receiver}{tx.amount}{tx.nonce}'.encode()).hexdigest()
        tx.tx_id = hashlib.sha256(f'{hexlify(tx.public_key_bin)}{tx.nonce}'.encode()).hexdigest()

        self.sign_transaction(tx)
        self.counter += 1
        self.pending_txs.append(tx)

        for peer in list(self.get_peers()):
            self.ez_send(peer, tx)
            
        if self.counter > self.max_messages:
            self.cancel_pending_task("tx_create")
            self.stop()
            return
        
    def web_uniswap_transaction(self, coin, amount = 10):
        tx = Transaction(self.node_id, self.node_id, is_uniswap=True, coin=coin, amount=amount, public_key_bin=b'', signature=b'', tx_id='', nonce=self.counter)
        tx.public_key_bin = self.my_peer.public_key.key_to_bin()
        # tx.tx_id = hashlib.sha256(f'{tx.sender}{tx.receiver}{tx.amount}{tx.nonce}'.encode()).hexdigest()
        tx.tx_id = hashlib.sha256(f'{hexlify(tx.public_key_bin)}{tx.nonce}'.encode()).hexdigest()

        self.sign_transaction(tx)
        self.counter += 1
        self.pending_txs.append(tx)

        if coin == 'BTC':
            self.pools['BTC'] = self.pools['BTC']+tx.amount
            self.pools['ETH'] = self.c/self.pools['BTC']
            self.balances['BTC'] -= 10
        else:
            self.pools['ETH'] = self.pools['ETH'] + tx.amount
            self.pools['BTC'] = self.c / self.pools['ETH']
            self.balances['ETH'] -= 10

        for peer in list(self.get_peers()):
            self.ez_send(peer, tx)

        if self.counter > self.max_messages:
            self.cancel_pending_task("tx_create")
            self.stop()
            return

    def create_uniswap_transaction(self, coin):
        tx = Transaction(self.node_id, self.node_id, is_uniswap=True, coin=coin, public_key_bin=b'', signature=b'', tx_id='', nonce=self.counter)
        tx.public_key_bin = self.my_peer.public_key.key_to_bin()
        # tx.tx_id = hashlib.sha256(f'{tx.sender}{tx.receiver}{tx.amount}{tx.nonce}'.encode()).hexdigest()
        tx.tx_id = hashlib.sha256(f'{hexlify(tx.public_key_bin)}{tx.nonce}'.encode()).hexdigest()

        self.sign_transaction(tx)
        self.counter += 1
        self.pending_txs.append(tx)

        if coin == 'BTC':
            self.pools['BTC'] -= tx.amount
            self.pools['ETH'] += tx.amount
        else:
            self.pools['BTC'] += tx.amount
            self.pools['ETH'] -= tx.amount

        for peer in list(self.get_peers()):
            self.ez_send(peer, tx)

        if self.counter > self.max_messages:
            self.cancel_pending_task("tx_create")
            self.stop()
            return

    def append_block(self, block: Block):
        self.blocks.append(block)
        self.blocks.sort(key=lambda x: x.number)
        self.find_optimal_chain()

    def broadcast_current_block(self):
        self.logger.info(f'Node {self.node_id} is broadcasting self.curr_block! {self.curr_block.number}')

        for peer in list(self.get_peers()):
            self.ez_send(peer, self.curr_block)

    def find_optimal_chain(self):
        # Initialize variables to store chains and remaining blocks
        chains = []
        blocks_still_not_in_chain = self.blocks.copy()

        # Iterate while there are still blocks not added to any chain
        while blocks_still_not_in_chain:
            # Start a new chain with the first block in the list
            current_chain = [blocks_still_not_in_chain.pop(0)]

            # Try to extend the chain
            i = 0
            while i < len(blocks_still_not_in_chain):
                block = blocks_still_not_in_chain[i]
                if block.prev_block_hash == current_chain[-1].hash:
                    current_chain.append(block)
                    blocks_still_not_in_chain.pop(i)
                else:
                    i += 1

            # Append the current chain to the list of chains
            chains.append(current_chain)

        # Debugging output to trace chains
        try:
            print(f'Node {self.node_id} has {len(chains)} chains')
            self.logger.info(f'Node {self.node_id} has {len(chains)} chains')
            for chain in chains:
                self.logger.info(f'Chain length: {len(chain)}')
                for block in chain:
                    self.logger.info(f'Block number: {block.number}, hash: {block.hash}')
        except Exception as e:
            self.logger.info(f"An error occurred while printing chain details: {e}")

    def check_curr_block(self) :
        self.logger.info(f'Node {self.node_id} is checking self.curr_block!')

        for txs in self.pending_txs:
            result = self.curr_block.add_transaction(txs)

            if result == False:
                self.logger.info(f'{self.node_id} has full cur_block!')

                self.cancel_pending_task("mine_block")
                self.register_mine_task()

                self.logger.info(f'Node {self.node_id} created new block with number {self.curr_block.number}')
                self.logger.info(f'node {self.node_id} has the following blocks: {[block.number for block in self.blocks]}')

    def on_start(self):
        # self.start_client()
        self.start_validator()

    def start_client(self):
        # Create transaction and send to random validator
        # Or put node_id
        self.register_task("tx_create",
                           self.create_transaction, delay=1,
                           interval=1)
        self.register_task("process_pending_txs",
                           self.check_curr_block, delay=1,
                           interval=1)

    def register_mine_task(self):
        self.register_task("mine_block", self.mine)

    def mine(self):
        now = time.time()
        # loop = asyncio.get_event_loop()
        self.logger.info(f'Someone is mining block {self.curr_block.number}...')
        while True:
            self.curr_block.hashing_value = self.curr_block.get_hashing_value(self.my_peer.public_key.key_to_bin())
            self.curr_block.hash = hashlib.sha256(self.curr_block.hashing_value.encode()).hexdigest()
            # Use 2^target for comparison
            target_value = 2 ** Decimal(self.curr_block.puzzle_target)

            if int(self.curr_block.hash, 16) < target_value:
                self.curr_block.time = int(self.curr_block.prev_block_time + time.time() - now)
                self.logger.info(f'Block {self.curr_block.number} is mined. Here is hash: {self.curr_block.hash}')
                self.logger.info(f'Block {self.curr_block.number} based on hashing value:{self.curr_block.hashing_value}')
                self.logger.info(f'Block {self.curr_block.number} based on nonce:{self.curr_block.nonce}')
                self.logger.info(f'It took {time.time() - now} seconds to mine this block {self.curr_block.number}')
                self.append_block(self.curr_block)
                self.update_pending_finalized_txs(self.curr_block)
                for peer in self.get_peers():
                    self.logger.info(f'sending block {self.curr_block.number}')
                    self.ez_send(peer, self.curr_block)
                self.create_block()
                return self.curr_block.hash
            self.curr_block.nonce += 1
    def start_validator(self):
        self.register_task("check_txs", self.check_transactions, delay=2, interval=1)

    def check_transactions(self):
        for tx in self.pending_txs:
            # block = self.find_block_for_transaction(tx)
            if tx.is_uniswap == False:
                if self.balances[tx.sender][tx.coin] - tx.amount >= 0:
                    self.balances[tx.sender][tx.coin] -= tx.amount
                    self.balances[tx.receiver][tx.coin] += tx.amount
                    # self.pending_txs.remove(tx)
                    # self.finalized_txs.append(tx)
            else:
                if tx.coin == "ETH":
                    if self.balances[tx.sender][tx.coin] - tx.amount >= 0:
                        self.balances[tx.sender][tx.coin] -= tx.amount
                        self.balances[tx.receiver]["BTC"] += tx.amount
                else:
                    if self.balances[tx.sender][tx.coin] - tx.amount >= 0:
                        self.balances[tx.sender][tx.coin] -= tx.amount
                        self.balances[tx.receiver]["ETH"] += tx.amount



        self.executed_checks += 1

        if self.executed_checks > 5:
            self.cancel_pending_task("check_txs")
            balances_output = ', '.join([f'({key}, {value})' for key, value in self.balances.items()])
            print(f'balances:  {balances_output}')
            self.logger.info(f'balances:  {balances_output}')
            print(f'amount of transactions: {len(self.curr_block.transactions)}')
            # self.logger.info(f'amount of transactions: {len(self.curr_block.transactions)}')
            self.logger.info(f'node id: {self.node_id}, self.pending_txs length: {len(self.pending_txs)}, '
                        f'self.finalized_txs length: {len(self.finalized_txs)}, number of collision: {self.collision_num}')
            self.stop()

    def verify_block(self, block: Block) -> bool:
        return True
        # if block.hash != hashlib.sha256(block.get_hashing_value().encode()).hexdigest() \
        #         and int(block.hash, 16) < float(self.puzzle_target):
        #     return False
        # else:
        #     return True

    def send_web_transaction(self, peer_recipient, amount = 10):
        tx = Transaction(self.node_id, peer_recipient, amount, b'', b'', '', self.counter)
        tx.public_key_bin = self.my_peer.public_key.key_to_bin()
        tx.tx_id = hashlib.sha256(f'{hexlify(tx.public_key_bin)}{tx.nonce}'.encode()).hexdigest()

        self.sign_transaction(tx)
        self.counter += 1
        self.pending_txs.append(tx)

        for peer in list(self.get_peers()):
            self.ez_send(peer, tx)

        if self.counter > self.max_messages:
            self.cancel_pending_task("tx_create")
            self.stop()
            return

    @message_wrapper(Transaction)
    async def on_transaction(self, peer: Peer, payload: Transaction) -> None:
        print(self.node_id, payload.ttl)
        if self.verify_signature(payload):

            # Add to pending transactions if signature is verified
            print(f'transaction nonce:{payload.nonce}')
            self.logger.info(f'transaction nonce:{payload.nonce}')
            print(f'[Node {self.node_id}] Received transaction {payload.nonce} from {self.node_id_from_peer(peer)}')
            self.logger.info(f'[Node {self.node_id_from_peer(peer)}] -> [Node {self.node_id}] TTL: {payload.ttl} amount: {payload.amount} VAD ')
            
            if (hexlify(payload.public_key_bin), payload.nonce) not in [(hexlify(tx.public_key_bin), tx.nonce) for tx in
                                                                        self.finalized_txs] and (
                    hexlify(payload.public_key_bin), payload.nonce) not in [(hexlify(tx.public_key_bin), tx.nonce) for
                                                                            tx in self.pending_txs]:

                self.pending_txs.append(payload)
                self.logger.info(
                    f'Node {self.node_id} already have {len(self.finalized_txs)} from finalized and {len(self.pending_txs)} in pending')
                self.check_curr_block()
            else:
                self.collision_num += 1
                pass
            
            if payload.ttl > 1:
                payload.ttl -= 1
                # Gossip to other nodes
                for peer in list(self.get_peers()):
                    print(
                        f'[Node {self.node_id}] sending transaction {payload.nonce} with TTL: {payload.ttl} for {self.node_id_from_peer(peer)}')
                    self.ez_send(peer, payload)

    def create_blocks_request(self, sender, start_block_number, end_block_number):
        request = BlocksRequest(sender, start_block_number, end_block_number)
        return request

    def update_pending_finalized_txs(self, block):
        # we need to remove from pending_txs transactions that were already included in mined block
        self.logger.info(f'Node {self.node_id} Updating of pending_txs and finalized_txs............')
       
        for tx in self.pending_txs:
            if tx not in block.transactions:
                self.pending_txs.remove(tx)
                self.finalized_txs.append(tx)

    def clean_curr_block_txs(self, payload):
        # we need to remove transactions included in mined block from out curr_block.transactions
        self.logger.info(f'Node {self.node_id} Cleaning of self.curr_block_txs............')
        new_txs_list = []

        for tx in payload.transactions:
            if tx not in self.curr_block.transactions:
                new_txs_list.append(tx)

        self.curr_block.transactions = new_txs_list

    @message_wrapper(Block)
    def on_block(self, peer: Peer, payload: Block) -> None:
        if self.verify_block(payload):
            print(f'[Node {self.node_id}] Received block {payload.number} from [Node {self.node_id_from_peer(peer)}]')
            self.logger.info(
                f'[Node {self.node_id}] Received block {payload.number} from [Node {self.node_id_from_peer(peer)}]')

        #     # pull gossip
        #     prev_block_number = 0 if len(self.blocks) == 0 else self.blocks[-1].number
        #     if (payload.number - prev_block_number == 1):
        #         self.logger.info('we received block  that we can append')
        #         # we received block  that we can append
        #         self.blocks.append(payload)
        #         self.update_pending_finalized_txs(payload)
        #         self.clean_curr_block_txs(payload)
            self.append_block(payload)
            # only if the block is for longest chain
            self.update_pending_finalized_txs(payload)
            self.clean_curr_block_txs(payload)
            self.check_curr_block()

        #         # broadcast to all peers
        #         for peer in self.get_peers():
        #             self.ez_send(peer, payload)
        #     elif (payload.number - prev_block_number) < 1:
        #         self.logger.info('we received block that we already have')
        #         # we already have this block, then
        #         # broadcast to all peers
        #         for peer in self.get_peers():
        #             self.ez_send(peer, payload)
        #     else:
        #         # we received block that we don't have
        #         # and it cannot be appended
        #         self.update_pending_finalized_txs(payload)
        #         self.clean_curr_block_txs(payload)

        #         start_block_number = self.blocks[-1].number + 1
        #         end_block_number = payload.number

        #         self.logger.info(
        #             f'we received block that we dont have, need request from block from {start_block_number} to {end_block_number}')
        #         request_message = self.create_blocks_request(self.node_id, start_block_number, end_block_number)

            #     for peer in self.get_peers():
            #         self.ez_send(peer, request_message)

            # self.logger.info(f'Node {self.node_id} has the following blocks: {[block.number for block in self.blocks]}')

    @message_wrapper(BlocksRequest)
    def on_blocks_request(self, peer: Peer, payload: BlocksRequest) -> None:
        self.logger.info(f'Node {self.node_id} has the following blocks: {[block.number for block in self.blocks]}')
        self.logger.info(
            f'Node {self.node_id} received block request from {payload.start_block_number} to {payload.end_block_number}')
        last_possible_block_number = min(payload.end_block_number + 1, self.blocks[-1].number)

        for i in range(payload.start_block_number, last_possible_block_number):
            self.ez_send(payload.sender, self.blocks[i])

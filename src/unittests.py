import unittest
from ipv8.community import CommunitySettings
from ipv8.overlay import Settings

from algorithms.blockchain import Transaction, Block, BlockchainNode, Blockchain
import hashlib
import asyncio


class TestTransaction(unittest.TestCase):
    def test_transaction_id(self):
        transaction = Transaction(sender=1, receiver=2, amount=100, public_key_bin=b'public_key', signature=b'signature')
        self.assertEqual(hashlib.sha256(f'{transaction.sender}{transaction.receiver}{transaction.amount}{transaction.nonce}'.encode()).hexdigest(), hashlib.sha256('121001'.encode()).hexdigest())


class TestBlock(unittest.TestCase):
    def setUp(self):
        self.block = Block(number=1, prev_block_time=1625097600, prev_block_hash='0', difficulty=1, puzzle_target=2, transactions=[])

    def test_add_transaction(self):
        transaction = Transaction(sender=1, receiver=2, amount=50, public_key_bin=b'key', signature=b'sig')
        self.block.add_transaction(transaction)
        self.assertIn(transaction, self.block.transactions)

    def test_mine_block(self):
        asyncio.run(self.async_test_mine_block())

    async def async_test_mine_block(self):
        transaction = Transaction(sender=1, receiver=2, amount=50, public_key_bin=b'key', signature=b'sig')
        self.block.add_transaction(transaction)
        mined_hash = await self.block.mine()
        self.assertTrue(int(mined_hash, 16) < self.block.puzzle_target)


# class TestBlockchainNode(unittest.TestCase):
#     def setUp(self):
#         settings = CommunitySettings()
#         self.node = BlockchainNode(settings)
#
#     def test_create_transaction(self):
#         initial_count = len(self.node.pending_txs)
#         self.node.create_transaction()
#         self.assertEqual(len(self.node.pending_txs), initial_count + 1)
#
#     def test_verify_signature(self):
#         transaction = Transaction(sender=1, receiver=2, amount=100, public_key_bin=self.node.my_peer.public_key.key_to_bin(), signature=b'', nonce=1)
#         self.node.sign_transaction(transaction)
#         self.assertTrue(self.node.verify_signature(transaction))
#
#     def test_process_pending_transactions(self):
#         transaction = Transaction(sender=1, receiver=2, amount=50, public_key_bin=b'key', signature=b'sig')
#         self.node.pending_txs.append(transaction)
#         self.node.process_pending_transactions()
#         self.assertIn(transaction, self.node.curr_block.transactions)


if __name__ == '__main__':
    unittest.main()

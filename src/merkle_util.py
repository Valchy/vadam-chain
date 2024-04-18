import hashlib


def hash_pair(a, b):
    return hashlib.sha256(a.encode() + b.encode()).hexdigest()

def merkle_root(transactions):
    if not transactions:
        return None
    if len(transactions) == 1:
        return transactions[0]
    if len(transactions) % 2 == 1:
        transactions.append(transactions[-1])
    new_level = []
    for i in range(0, len(transactions), 2):
        new_level.append(hash_pair(transactions[i], transactions[i+1]))
    return merkle_root(new_level)

def merkle_proof(transaction, block_transactions):
    if transaction not in block_transactions:
        return False
    if len(block_transactions) == 1:
        return transaction == block_transactions[0]
    if len(block_transactions) % 2 == 1:
        block_transactions.append(block_transactions[-1])
    new_level = []
    index = block_transactions.index(transaction)
    if index % 2 == 0:
        sibling = block_transactions[index + 1]
        new_transaction = hash_pair(transaction, sibling)
    else:
        sibling = block_transactions[index - 1]
        new_transaction = hash_pair(sibling, transaction)
    for i in range(0, len(block_transactions), 2):
        if i != index and i+1 != index:
            new_level.append(hash_pair(block_transactions[i], block_transactions[i+1]))
    new_level.append(new_transaction)
    return merkle_proof(new_transaction, new_level)
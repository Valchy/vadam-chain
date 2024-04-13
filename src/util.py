import yaml
import copy
import argparse
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Scale the docker-compose file',
        description='Scale the number of nodes',
        epilog='Designed for A27 Fundamentals and Design of Blockchain-based Systems')
    parser.add_argument('num_nodes', type=int)
    parser.add_argument('topology_file', type=str, nargs='?', default='topologies/ring.yaml')
    parser.add_argument('algorithm', type=str, nargs='?', default='echo')
    parser.add_argument('template_file', type=str, nargs='?', default='docker-compose.template.yml')
    args = parser.parse_args()

    with open(args.template_file, 'r') as f:
        content = yaml.safe_load(f)

        node = content['services']['node0']
        content['x-common-variables']['TOPOLOGY'] = args.topology_file

        nodes = {}
        baseport = 9090
        connections = {}

        # Create a ring topology
        for i in range(args.num_nodes):
            n = copy.deepcopy(node)
            n['ports'] = [f'{baseport + i}:{baseport + i}']
            n['networks']['vpcbr']['ipv4_address'] = f'192.168.55.{10 + i}'
            n['environment']['PID'] = i
            n['environment']['TOPOLOGY'] = args.topology_file
            n['environment']['ALGORITHM'] = args.algorithm
            nodes[f'node{i}'] = n

            connections[i] = [j for j in range(args.num_nodes) if j != i]

        content['services'] = nodes

        with open('docker-compose.yml', 'w') as f2:
            yaml.safe_dump(content, f2)
            print(f'Output written to docker-compose.yml')

        with open(args.topology_file, 'w') as f3:
            yaml.safe_dump(connections, f3)
            print(f'Output written to {args.topology_file}')

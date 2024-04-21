import random

def generate_ring_topology(num_nodes):
    topology = [[] for _ in range(num_nodes)]  # Initialize an empty list for each node
    # create ring topology
    for i in range(num_nodes):
        topology[i].append((i - 1) % num_nodes)
        topology[i].append((i + 1) % num_nodes)
    # for i in range(num_nodes):
    #     for j in range(num_connections - len(topology[i])):
    #         connected_node = random.randint(0, num_nodes - 1)
    return topology


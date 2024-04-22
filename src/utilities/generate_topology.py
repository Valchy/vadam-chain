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


def generate_topology(topology, wanted_connections_num):
    for idx, connection_list in enumerate(topology):
        for i in range(wanted_connections_num - len(connection_list)):
            new_connection_node = random.randint(0, len(topology) - 1)
            new_node_added = False
            attempt = 0
            while not new_node_added :
                attempt += 1
                if attempt > 20:
                    # print(f'node: {i}')
                    break
                if new_connection_node == idx:
                    continue
                check_first = new_connection_node in connection_list
                if not check_first:
                    connection_list.append(new_connection_node)
                    new_node_added = True
                    topology[new_connection_node].append(idx)
                new_connection_node = random.randint(0, len(topology) - 1)
    return topology

# print(generate_ring_topology(10))
print(generate_topology(generate_ring_topology(10), 5))

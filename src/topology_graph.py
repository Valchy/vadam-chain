import networkx as nx
import matplotlib.pyplot as plt
import random

def generate_topology(num_nodes, max_peers, min_peers, connection_probability):
    """
    Generates a graph with specified number of nodes, ensuring each node has connections between min_peers and max_peers.
    """
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    
    for node in range(num_nodes):
        # Start by establishing the minimum required connections
        connected_peers = []
        while len(connected_peers) < min_peers:
            target = random.randint(0, num_nodes - 1)
            if node != target and target not in connected_peers and not G.has_edge(node, target):
                G.add_edge(node, target)
                connected_peers.append(target)

        # Add additional edges with the specified probability without exceeding max_peers
        potential_connections = list(set(range(num_nodes)) - set(connected_peers) - {node})
        random.shuffle(potential_connections)
        
        current_connections = len(connected_peers)
        for target in potential_connections:
            if random.random() < connection_probability and current_connections < max_peers:
                G.add_edge(node, target)
                current_connections += 1
                if current_connections >= max_peers:
                    break

    return G

def draw_graph(G, title, file_name):
    """
    Draws the graph using matplotlib and saves it to a file.
    """
    plt.figure(figsize=(12, 10))
    pos = nx.circular_layout(G)  # Changed to use circular layout
    plt.title(title)
    nx.draw(G, pos, node_color='lightblue', with_labels=True, node_size=500, font_weight='bold', edge_color='gray')
    plt.savefig(file_name)
    plt.close()

# Number of nodes
nodes = 100

# Sparse topology parameters (min 1, max 6 connections)
sparse_graph = generate_topology(nodes, max_peers=6, min_peers=1, connection_probability=0.02)
draw_graph(sparse_graph, "Sparse Topology with 100 Nodes (1-6 connections per node)", "./graphs/sparse_topology.png")

# Dense topology parameters (min 1, max 16 connections)
dense_graph = generate_topology(nodes, max_peers=16, min_peers=1, connection_probability=0.05)
draw_graph(dense_graph, "Dense Topology with 100 Nodes (1-16 connections per node)", "./graphs/dense_topology.png")

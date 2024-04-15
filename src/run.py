import argparse
import yaml
from asyncio import run
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, Bootstrapper, BootstrapperDefinition, default_bootstrap_defs
from ipv8.util import create_event_with_signals
from ipv8_service import IPv8
from algorithms import *
from da_types import Blockchain


def get_algorithm(name: str) -> Blockchain:
    algorithms = {
        'echo': EchoAlgorithm,
        'election': RingElection,
        'blockchain': BlockchainNode,
    }
    if name not in algorithms.keys():
        raise Exception(f'Cannot find select algorithm with name {name}')
    return algorithms[name]

async def start_communities(node_id, connections, algorithm, use_localhost=True, dense=False) -> None:
    event = create_event_with_signals()
    base_port = 9090
    connections_updated = [(x, base_port + x) for x in connections]
    node_port = base_port + node_id
    config = ConfigBuilder().clear_keys().clear_overlays()
    config.add_key("my peer", "medium", f"ec{node_id}.pem")
    config.set_port(node_port)

    # Changing default rules of IPv8 to create sparse or dense topology
    if dense:
        # Dense topology: maximize connections
        walker = WalkerDefinition(strategy=Strategy.RandomWalk, peers=-1, init={'timeout': 3.0})
        bootstrapper = BootstrapperDefinition(bootstrapper=Bootstrapper.DispersyBootstrapper, init={'max_peers': 16})
    else:
        # Sparse topology: limit connections
        walker = WalkerDefinition(strategy=Strategy.RandomWalk, peers=-1, init={'timeout': 10.0})
        bootstrapper = BootstrapperDefinition(bootstrapper=Bootstrapper.DispersyBootstrapper, init={'max_peers': 6})

    # Add overlay to config
    config.add_overlay(
        overlay_class='blockchain_community',
        key_alias='my peer',
        walkers=[walker],
        bootstrappers=[bootstrapper],
        initialize={},
        on_start=[("started", node_id, connections_updated, event, use_localhost)],
    )

    # Initialise config with ipv8 instance
    ipv8_instance = IPv8(
        config.finalize(), extra_communities={"blockchain_community": algorithm}
    )

    await ipv8_instance.start()
    await event.wait()
    await ipv8_instance.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Blockchain",
        description="Code to execute blockchain.",
        epilog="Designed for A27 Fundamentals and Design of Blockchain-based Systems",
    )
    parser.add_argument("node_id", type=int)
    parser.add_argument("topology", type=str, nargs="?", default="topologies/default.yaml")
    parser.add_argument("algorithm", type=str, nargs="?", default='echo')
    parser.add_argument("-docker", action='store_true')
    args = parser.parse_args()
    node_id = args.node_id

    alg = get_algorithm(args.algorithm)
    with open(args.topology, "r") as f:
        topology = yaml.safe_load(f)
        connections = topology[node_id]

        run(start_communities(node_id, connections, alg, not args.docker))

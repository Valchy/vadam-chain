# Command to run file from console
# Don't forget to pip install -r requirements.txt before running commands below
# WINDOWS: source .venv/Scripts/activate; cd src; python run_local.py
# MAC: source .venv/bin/activate; cd src; python3 run_local.py

from asyncio import run
import threading

from ipv8.configuration import ConfigBuilder, default_bootstrap_defs
from ipv8.util import run_forever, create_event_with_signals
from ipv8_service import IPv8

from blockchain import BlockchainNode
from server import run_web_server

from log.logging_config import *
from utilities.generate_topology import generate_ring_topology, generate_topology

# Create logger
setup_logging()
logger = logging.getLogger('my_app')

async def start_communities(peer_num, use_localhost=True) -> None:
    logger.info('Community started')
    base_port = 9090
    ipv8_instances = {}

    topology = generate_topology(generate_ring_topology(peer_num), 5)
    logger.info(f'topology : {topology}')

    for i in range(0, peer_num):
        event = create_event_with_signals()
        node_port = base_port + i

        connections = topology[i]
        connections_updated = [(x, base_port + x) for x in connections]

        builder = ConfigBuilder().clear_keys().clear_overlays()
        builder.add_key("my peer", "medium", f"ec{i}.pem")
        builder.set_port(node_port)
        builder.add_overlay("blockchain_community","my peer",[],default_bootstrap_defs,{},[("started", i, connections_updated, event, use_localhost)])

        ipv8_instance = IPv8(builder.finalize(), extra_communities={'blockchain_community': BlockchainNode})
        await ipv8_instance.start()

        logger.info(f'Node running on port {node_port}')
        ipv8_instances[node_port] = ipv8_instance
        print(ipv8_instance)

    fastapi_thread = threading.Thread(target=lambda: run_web_server(ipv8_instances))
    fastapi_thread.start()

    await run_forever()

if __name__ == "__main__":
    run(start_communities(3))

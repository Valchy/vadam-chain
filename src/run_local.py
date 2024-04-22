
from asyncio import run

from ipv8.configuration import ConfigBuilder, default_bootstrap_defs
from ipv8.util import run_forever, create_event_with_signals
from ipv8_service import IPv8

from algorithms.blockchain import BlockchainNode

from log.logging_config import *
from src.utilities.generate_topology import generate_ring_topology, generate_topology

setup_logging()

# Create logger
logger = logging.getLogger('my_app')
async def start_communities(peer_num, use_localhost=True) -> None:
    logger.info('Community started')
    base_port = 9090
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
        builder.add_overlay("blockchain_community",
                            "my peer",
                            [],
                            default_bootstrap_defs,
                            {},
                            [("started", i, connections_updated, event, use_localhost)],
                            )
        await IPv8(builder.finalize(),
                   extra_communities={'blockchain_community': BlockchainNode}).start()
    await run_forever()

run(start_communities(10))
import logging

from ...entities.node import Node
from ...utils.enums import NodeState

logger = logging.getLogger(__name__)


async def check_node_states():
    from ... import socketManager

    nodes: list[Node] = await Node.find_all().to_list()

    update_frontend = False

    for node in nodes:
        if node.state != NodeState.ERROR and node.is_timed_out():
            await node.on_timeout()
            update_frontend = True

    if update_frontend:
        logger.info("Detected node-state change(s), emitting 'change'")
        socketManager.emit("change-node")


async def trigger_socketio():
    from ... import socketManager

    await socketManager.periodic_trigger()

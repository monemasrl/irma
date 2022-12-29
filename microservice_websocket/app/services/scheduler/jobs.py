import logging

from ...services.database import Node
from ...utils.node import update_state

logger = logging.getLogger(__name__)


async def check_node_states():
    from ... import socketManager

    nodes: list[Node] = await Node.find_all().to_list()

    update_frontend = False

    for node in nodes:
        new_state = update_state(node.state, node.lastSeenAt)

        if node.state != new_state:
            update_frontend = True
            node.state = new_state
            await node.save()

    if update_frontend:
        logger.info("Detected node-state change(s), emitting 'change'")
        socketManager.emit("change-reading")
        socketManager.emit("change")


async def trigger_socketio():
    from ... import socketManager

    await socketManager.periodic_trigger()

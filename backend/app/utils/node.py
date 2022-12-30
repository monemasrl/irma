import logging
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from ..config import config as Config
from ..services.database import Application, Node, NodeSettings
from .enums import EventType, NodeState
from .exceptions import NotFoundException
from .node_settings import send_update_settings

logger = logging.getLogger(__name__)


def on_keep_alive(current_state: NodeState) -> NodeState:
    if current_state == NodeState.ERROR:
        return NodeState.READY

    return current_state


def update_state(
    current_state: NodeState,
    lastSeenAt: datetime,
    event: EventType | None = None,
) -> NodeState:

    if (datetime.now() - lastSeenAt) > timedelta(
        seconds=Config.app.NODE_TIMEOUT_INTERVAL
    ):
        return NodeState.ERROR

    if event is not None:
        if event == EventType.START_REC:
            current_state = NodeState.RUNNING
        elif event == EventType.STOP_REC:
            current_state = NodeState.READY
        elif event == EventType.RAISE_ALERT:
            current_state = NodeState.ALERT_READY
        elif event == EventType.HANDLE_ALERT:
            current_state = NodeState.READY
        elif event == EventType.KEEP_ALIVE:
            current_state = on_keep_alive(current_state)
        elif event == EventType.ON_LAUNCH:
            current_state = NodeState.READY
        else:
            logger.error(f"EventType '{event}' not implemented yet")

    return current_state


async def get_nodes(applicationID: str):
    application: Application | None = await Application.get(
        PydanticObjectId(applicationID)
    )
    if application is None:
        raise NotFoundException("Application")

    nodes: list[Node] = await Node.find(Node.application == application.id).to_list()

    return nodes


async def on_launch(node: Node):
    settings = await NodeSettings.find_one(NodeSettings.node == node.id)
    if settings is None:
        logger.info("No settings found for node: %s", node)
        return

    await send_update_settings(str(node.application), node.nodeID, settings)

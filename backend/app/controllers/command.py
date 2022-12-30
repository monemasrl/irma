import logging

from ..entities.node import Node
from ..exceptions import NotFoundException
from ..utils.enums import CommandType

logger = logging.getLogger(__name__)


async def handle_command(command: CommandType, applicationID: str, nodeID: int):
    node = await Node.from_id(nodeID, applicationID)
    if node is None:
        raise NotFoundException("Node")

    if command == CommandType.START_REC:
        node.start_rec()
    elif command == CommandType.STOP_REC:
        node.stop_rec()
    elif command == CommandType.SET_DEMO_1:
        node.set_demo_1()
    elif command == CommandType.SET_DEMO_2:
        node.set_demo_2()
    else:
        logger.error("CommandType '%s' for ui operations not implemented yet", command)

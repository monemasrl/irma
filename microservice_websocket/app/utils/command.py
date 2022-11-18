from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..config import TESTING
from ..services.database.models import Application, Node
from .enums import CommandType
from .exceptions import NotFoundException


async def send_mqtt_command(applicationID: str, nodeID: str, command: CommandType):
    application: Application | None = await Application.get(
        PydanticObjectId(applicationID)
    )
    if application is None:
        raise NotFoundException("Application")

    node: Node | None = await Node.find_one(
        And(Eq(Node.application, application.id), Eq(Node.nodeID, nodeID))
    )
    if node is None:
        raise NotFoundException("Node")

    topic: str = f"{applicationID}/{nodeID}/command"
    data: bytes = command.to_bytes(1, "big")

    if not TESTING:
        from .. import mqtt

        mqtt.publish(topic, data)

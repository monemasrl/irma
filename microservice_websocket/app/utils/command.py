import json
from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..services.database.models import Application, Node
from .enums import CommandType
from .exceptions import NotFoundException


def publish(topic: str, data: bytes | str):
    if isinstance(data, str):
        data = data.encode()

    from .. import mqtt

    if mqtt:
        mqtt.publish(topic, data)


async def handle_command(command: CommandType, applicationID: str, nodeID: int):
    await check_existence(applicationID, nodeID)

    if command == CommandType.START_REC:
        publish(f"{applicationID}/{nodeID}/command", "start:0")
    elif command == CommandType.STOP_REC:
        publish(f"{applicationID}/{nodeID}/command", "stop")
    elif command == CommandType.SET_DEMO_1:
        publish(f"{applicationID}/{nodeID}/command", "start:1")
    elif command == CommandType.SET_DEMO_2:
        publish(f"{applicationID}/{nodeID}/command", "start:2")
    else:
        raise Exception(
            f"CommandType '{command}' for ui operations not implemented yet"
        )


async def check_existence(applicationID: str, nodeID: int):
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


async def send_set_hv_command(
    applicationID: str, nodeID: int, detector: int, sipm: int, value: int
):
    await check_existence(applicationID, nodeID)

    data = json.dumps(
        {"type": "hv", "detector": detector, "sipm": sipm, "value": value}
    )

    publish(f"{applicationID}/{nodeID}/set", data)


async def send_set_window_low(
    applicationID: str,
    nodeID: int,
    detector: int,
    sipm: int,
    window_number: int,
    value: int,
):
    await check_existence(applicationID, nodeID)

    data = json.dumps(
        {
            "type": "window_low",
            "n": window_number,
            "detector": detector,
            "sipm": sipm,
            "value": value,
        }
    )

    publish(f"{applicationID}/{nodeID}/set", data)


async def send_set_window_high(
    applicationID: str,
    nodeID: int,
    detector: int,
    sipm: int,
    window_number: int,
    value: int,
):
    await check_existence(applicationID, nodeID)

    data = json.dumps(
        {
            "type": "window_high",
            "n": window_number,
            "detector": detector,
            "sipm": sipm,
            "value": value,
        }
    )

    publish(f"{applicationID}/{nodeID}/set", data)

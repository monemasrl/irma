from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..services.database.models import Application, Node
from .enums import CommandType
from .exceptions import NotFoundException


def publish(topic: str, data: bytes):
    from .. import mqtt

    if mqtt:
        publish(topic, data)


async def handle_command(command: CommandType, applicationID: str, nodeID: int):
    if command == CommandType.START_REC:
        await send_start_rec_command(applicationID, nodeID)
    elif command == CommandType.STOP_REC:
        await send_stop_rec_command(applicationID, nodeID)
    elif command == CommandType.SET_DEMO_1:
        await send_set_demo_1_command(applicationID, nodeID)
    elif command == CommandType.SET_DEMO_2:
        await send_set_demo_2_command(applicationID, nodeID)
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


async def send_start_rec_command(applicationID: str, nodeID: int):
    await check_existence(applicationID, nodeID)

    topic: str = f"{applicationID}/{nodeID}/rec"
    data = b"start"

    publish(topic, data)


async def send_stop_rec_command(applicationID: str, nodeID: int):
    await check_existence(applicationID, nodeID)

    topic: str = f"{applicationID}/{nodeID}/rec"
    data = b"stop"

    publish(topic, data)


async def send_set_demo_1_command(applicationID: str, nodeID: int):
    await check_existence(applicationID, nodeID)

    topic: str = f"{applicationID}/{nodeID}/demo"
    data = b"1"

    publish(topic, data)


async def send_set_demo_2_command(applicationID: str, nodeID: int):
    await check_existence(applicationID, nodeID)

    topic: str = f"{applicationID}/{nodeID}/demo"
    data = b"2"

    publish(topic, data)


async def send_set_hv_command(
    applicationID: str, nodeID: int, detector: int, sipm: int, value: int
):
    await check_existence(applicationID, nodeID)

    topic: str = f"{applicationID}/{nodeID}/{detector}/{sipm}/hv"
    data = str(value).encode()

    publish(topic, data)


async def send_set_window_low(
    applicationID: str,
    nodeID: int,
    detector: int,
    sipm: int,
    window_number: int,
    value: int,
):
    await check_existence(applicationID, nodeID)

    topic: str = f"{applicationID}/{nodeID}/{detector}/{sipm}/{window_number}/low"
    data = str(value).encode()

    publish(topic, data)


async def send_set_window_high(
    applicationID: str,
    nodeID: int,
    detector: int,
    sipm: int,
    window_number: int,
    value: int,
):
    await check_existence(applicationID, nodeID)

    topic: str = f"{applicationID}/{nodeID}/{detector}/{sipm}/{window_number}/high"
    data = str(value).encode()

    publish(topic, data)

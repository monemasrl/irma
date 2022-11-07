from datetime import datetime

from beanie import PydanticObjectId

from .. import mqtt
from ..blueprints.api.models import PublishPayload
from ..config import config
from ..services.database import Alert, Application, Node, Reading
from .enums import NodeState, PayloadType
from .exceptions import NotFoundException
from .node import update_state
from .sync_cache import add_to_cache

DISABLE_MQTT = False


async def publish(payload: PublishPayload):
    application: Application | None = await Application.get(
        PydanticObjectId(payload.applicationID)
    )
    if application is None:
        raise NotFoundException("Application")

    node: Node | None = await Node.find_one(
        Node.application == application and Node.nodeID == payload.nodeID
    )

    if node is None:
        node = Node(
            nodeID=payload.nodeID,
            application=application.id,
            nodeName=payload.nodeName,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await node.save()

    if payload.payloadType == PayloadType.TOTAL_READING:
        await handle_total_reading(node, payload)

    elif payload.payloadType == PayloadType.WINDOW_READING:
        await handle_window_reading(node, payload)

    data = payload.data
    value = data.value if data else 0

    node.lastSeenAt = datetime.now()
    node.state = update_state(
        node.state,
        node.lastSeenAt,
        payload.payloadType,
        value,
    )
    await node.save()


async def handle_total_reading(node: Node, record: PublishPayload):
    data = record.data
    # TODO: fix
    assert data

    reading: Reading | None = await Reading.find_one(
        Reading.node == node
        and Reading.readingID == data.readingID
        and Reading.canID == data.canID
        and Reading.sensorNumber == data.sensorNumber
    )

    if reading is None:
        reading = Reading(
            node=node.id,
            canID=data.canID,
            sensorNumber=data.sensorNumber,
            readingID=data.readingID,
            sessionID=data.sessionID,
            publishedAt=datetime.now(),
        )

    reading.dangerLevel = data.value
    await reading.save()
    add_to_cache(str(reading.id))

    if reading.dangerLevel >= config["ALERT_TRESHOLD"]:
        alert: Alert | None = await Alert.find_one(
            Alert.sessionID == reading.sessionID and not Alert.isHandled
        )

        if alert is None:
            alert = Alert(
                reading=reading.id,
                node=node.id,
                sessionID=reading.sessionID,
                isHandled=False,
                raisedAt=datetime.now(),
            )
            await alert.save()


async def handle_window_reading(node: Node, payload: PublishPayload):
    data = payload.data
    # TODO: FIX
    assert data

    reading: Reading | None = await Reading.find_one(
        Reading.node == node
        and Reading.readingID == data.readingID
        and Reading.canID == data.canID
        and Reading.sensorNumber == data.sensorNumber
    )

    if reading is None:
        reading = Reading(
            node=node.id,
            canID=data.canID,
            sensorNumber=data.sensorNumber,
            sessionID=data.sessionID,
            readingID=data.readingID,
            publishedAt=datetime.now(),
        )

    window_number = data.value

    if window_number == 1:
        reading.window1_count = data.count
    elif window_number == 2:
        reading.window2_count = data.count
    elif window_number == 3:
        reading.window3_count = data.count
    else:
        raise ValueError(f"Unexpected window_number: {window_number}")

    await reading.save()
    add_to_cache(str(reading.id))


async def send_mqtt_command(applicationID: str, nodeID: str, command: int):
    application: Application | None = await Application.get(
        PydanticObjectId(applicationID)
    )
    if application is None:
        raise NotFoundException("Application")

    node: Node | None = await Node.find_one(
        Node.application == application and Node.nodeID == nodeID
    )
    if node is None:
        raise NotFoundException("Node")

    topic: str = f"{applicationID}/{nodeID}/command"
    data: bytes = command.to_bytes(1, "big")

    if not DISABLE_MQTT:
        mqtt.publish(topic, data)

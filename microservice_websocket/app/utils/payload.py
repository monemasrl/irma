from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..blueprints.api.models import PublishPayload
from ..config import config as Config
from ..services.database import Alert, Application, Node, Reading
from .enums import EventType, NodeState, PayloadType
from .exceptions import NotFoundException
from .node import update_state
from .sync_cache import add_to_cache


async def publish(payload: PublishPayload):
    application: Application | None = await Application.get(
        PydanticObjectId(payload.applicationID)
    )
    if application is None:
        raise NotFoundException("Application")

    node: Node | None = await Node.find_one(
        And(Eq(Node.application, application.id), Eq(Node.nodeID, payload.nodeID))
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

    node.lastSeenAt = datetime.now()

    if payload.payloadType == PayloadType.TOTAL_READING:
        await handle_total_reading(node, payload)

    elif payload.payloadType == PayloadType.WINDOW_READING:
        await handle_window_reading(node, payload)
        node.state = update_state(node.state, node.lastSeenAt, EventType.START_REC)

    data = payload.data
    value = data.value if data else 0

    if (
        payload.payloadType == PayloadType.TOTAL_READING
        and value >= Config.app.ALERT_TRESHOLD
    ):
        node.state = update_state(node.state, node.lastSeenAt, EventType.RAISE_ALERT)
    else:
        node.state = update_state(
            node.state,
            node.lastSeenAt,
            EventType.KEEP_ALIVE,
        )
    await node.save()


async def handle_total_reading(node: Node, record: PublishPayload):
    data = record.data
    # TODO: fix
    assert data

    reading: Reading | None = await Reading.find_one(
        And(
            Eq(Reading.node, node.id),
            Eq(Reading.readingID, data.readingID),
            Eq(Reading.canID, data.canID),
            Eq(Reading.sensorNumber, data.sensorNumber),
        )
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

    if reading.dangerLevel >= Config.app.ALERT_TRESHOLD:
        alert: Alert | None = await Alert.find_one(
            And(Eq(Alert.sessionID, reading.sessionID), Eq(Alert.isHandled, False))
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
        And(
            Eq(Reading.node, node.id),
            Eq(Reading.readingID, data.readingID),
            Eq(Reading.canID, data.canID),
            Eq(Reading.sensorNumber, data.sensorNumber),
        )
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

    if window_number == 0:
        reading.window1 = data.count
    elif window_number == 1:
        reading.window2 = data.count
    elif window_number == 2:
        reading.window3 = data.count
    else:
        raise ValueError(f"Unexpected window_number: {window_number}")

    await reading.save()
    add_to_cache(str(reading.id))

from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..config import config as Config
from ..models.payload import ReadingPayload
from ..services.database import Alert, Application, Node, Reading
from .enums import EventType, NodeState
from .node import update_state


async def handle_payload(payload: ReadingPayload):
    from .. import socketManager

    application: Application | None = await Application.get(
        PydanticObjectId(payload.applicationID)
    )
    if application is None:
        print(f"Application '{payload.applicationID}' not found")
        return

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
    new_state = node.state
    changed = False

    if payload.payloadType == "total":
        await handle_total_reading(node, payload)

    elif payload.payloadType == "window":
        await handle_window_reading(node, payload)
        new_state = update_state(new_state, node.lastSeenAt, EventType.START_REC)

    data = payload.data
    value = data.value if data else 0

    if payload.payloadType == "total" and value >= Config.app.ALERT_TRESHOLD:
        new_state = update_state(new_state, node.lastSeenAt, EventType.RAISE_ALERT)
    else:
        new_state = update_state(
            new_state,
            node.lastSeenAt,
            EventType.KEEP_ALIVE,
        )

    changed = new_state != node.state
    node.state = new_state

    await node.save()

    if changed:
        socketManager.emit("changed")


async def handle_total_reading(node: Node, payload: ReadingPayload):
    data = payload.data

    reading = Reading(
        node=node.id,
        canID=data.canID,
        sensor_number=data.sensorNumber,
        readingID=data.readingID,
        sessionID=data.sessionID,
        published_at=datetime.now(),
        name="t",
        value=data.value,
    )
    await reading.save()

    if data.value >= Config.app.ALERT_TRESHOLD:
        alert: Alert | None = await Alert.find_one(
            And(Eq(Alert.sessionID, data.sessionID), Eq(Alert.isHandled, False))
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


async def handle_window_reading(node: Node, payload: ReadingPayload):
    data = payload.data

    window_number = data.value
    if window_number == 0:
        name = "w1"
    elif window_number == 1:
        name = "w2"
    elif window_number == 2:
        name = "w3"
    else:
        raise ValueError(f"Unexpected window_number: {window_number}")

    reading = Reading(
        node=node.id,
        canID=data.canID,
        sensor_number=data.sensorNumber,
        readingID=data.readingID,
        sessionID=data.sessionID,
        published_at=datetime.now(),
        name=name,
        value=data.count,
    )

    await reading.save()

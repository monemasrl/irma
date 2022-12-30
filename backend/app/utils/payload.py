import logging
from datetime import datetime

from beanie.operators import And, Eq

from ..config import config as Config
from ..models.payload import ReadingPayload
from ..services.database import Alert, Node, Reading

logger = logging.getLogger(__name__)


async def handle_payload(node: Node, payload: ReadingPayload):
    from .. import socketManager

    changed = False

    if payload.payloadType == "total":
        await handle_total_reading(node, payload)

    elif payload.payloadType == "window":
        await handle_window_reading(node, payload)
        await node.on_start_rec()
        changed = True

    data = payload.data
    value = data.value if data else 0

    if payload.payloadType == "total" and value >= Config.app.ALERT_TRESHOLD:
        await node.on_alert()
        changed = True

    if changed:
        socketManager.emit("change-node")


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
        logger.error("Unexpected window_number: %s", window_number)
        return

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

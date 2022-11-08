from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..blueprints.api.models import AlertInfo, HandlePayload
from ..services.database import Alert, Node, Reading, User
from .exceptions import NotFoundException
from .node import update_state
from .payload import PayloadType


async def handle_alert(payload: HandlePayload, user: User):
    alert: Alert | None = await Alert.get(PydanticObjectId(payload.alertID))
    if alert is None:
        raise NotFoundException("Alert")

    node: Node | None = await Node.get(PydanticObjectId(alert.node))
    if node is None:
        raise NotFoundException("Node")

    alert.isConfirmed = payload.isConfirmed
    alert.isHandled = True
    alert.handledBy = user.id
    alert.handledAt = datetime.now()
    alert.handleNote = payload.handleNote
    await alert.save()

    if (
        await Alert.find_one(And(Eq(Alert.node, node.id), Eq(Alert.isHandled, False)))
    ) is None:
        node.state = update_state(node.state, node.lastSeenAt, PayloadType.HANDLE_ALERT)
        await node.save()

    return alert


async def alert_info(alert_id: str) -> AlertInfo:
    alert: Alert | None = await Alert.get(PydanticObjectId(alert_id))
    if alert is None:
        raise NotFoundException("Alert")

    reading: Reading | None = await Reading.get(alert.reading)
    if reading is None:
        raise NotFoundException("Reading")

    node: Node | None = await Node.get(alert.node)
    if node is None:
        raise NotFoundException("Node")

    return AlertInfo(
        nodeID=node.nodeID,
        sessionID=reading.sessionID,
        readingID=reading.readingID,
        canID=reading.canID,
        alertID=alert_id,
        raisedAt=int(alert.raisedAt.timestamp()),
    )

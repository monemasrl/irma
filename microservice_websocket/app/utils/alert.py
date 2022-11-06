from datetime import datetime

from beanie import PydanticObjectId

from ..blueprints.api.models import HandlePayload
from ..services.database import Alert, Node, Reading, User
from ..services.database.utils import fetch_or_raise
from .exceptions import NotFoundException
from .node import update_state
from .payload import PayloadType


async def handle_alert(payload: HandlePayload, user: User):
    alert: Alert | None = await Alert.get(PydanticObjectId(payload.alertID))
    if alert is None:
        raise NotFoundException("Alert")

    node = await fetch_or_raise(alert.node)

    alert.isConfirmed = payload.isConfirmed
    alert.isHandled = True
    alert.handledBy = User.link_from_id(user.id)
    alert.handledAt = datetime.now()
    alert.handleNote = payload.handleNote
    await alert.save()

    if await Alert.find_one(Alert.node == node and not Alert.isHandled) is None:
        node.state = update_state(node.state, node.lastSeenAt, PayloadType.HANDLE_ALERT)
        await node.save()

    return alert


async def alert_info(alert_id: str) -> dict:
    alert: Alert | None = await Alert.get(PydanticObjectId(alert_id))
    if alert is None:
        raise NotFoundException("Alert")

    reading: Reading = await fetch_or_raise(alert.reading)
    node: Node = await fetch_or_raise(alert.node)

    return {
        "nodeID": node.nodeID,
        "sessionID": reading.sessionID,
        "readingID": reading.readingID,
        "canID": reading.canID,
        "alertID": alert_id,
        "raisedAt": int(alert.raisedAt.timestamp()),
    }

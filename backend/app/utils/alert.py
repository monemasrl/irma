from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..blueprints.api.models import HandlePayload
from ..services.database import Alert, Node, User
from .enums import EventType
from .exceptions import NotFoundException
from .node import update_state


async def handle_alert(alertID: str, payload: HandlePayload, user: User):
    alert: Alert | None = await Alert.get(PydanticObjectId(alertID))
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
        node.state = update_state(node.state, node.lastSeenAt, EventType.HANDLE_ALERT)
        await node.save()

    return alert


async def get_alert(alert_id: str) -> Alert:
    alert: Alert | None = await Alert.get(PydanticObjectId(alert_id))
    if alert is None:
        raise NotFoundException("Alert")

    return alert

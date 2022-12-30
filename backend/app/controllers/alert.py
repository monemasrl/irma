from datetime import datetime

from beanie import PydanticObjectId

from ..exceptions import NotFoundException
from ..routes.models import HandlePayload
from ..services.database import Alert, Node, User


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

    await node.on_handle()


async def get_alert(alert_id: str) -> Alert:
    alert: Alert | None = await Alert.get(PydanticObjectId(alert_id))
    if alert is None:
        raise NotFoundException("Alert")

    return alert

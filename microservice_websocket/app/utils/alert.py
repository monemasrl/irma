from datetime import datetime

from ..services.database import Alert, User
from .exceptions import ObjectNotFoundException
from .node import update_state
from .payload import PayloadType


def handle_alert(received: dict, user_id: str):
    alert = Alert.objects(id=received["alertID"]).first()

    if alert is None:
        raise ObjectNotFoundException(Alert)

    node = alert["node"]
    user = User.objects(id=user_id).first()

    alert["isConfirmed"] = received["isConfirmed"]
    alert["isHandled"] = True
    alert["handledBy"] = user
    alert["handledAt"] = datetime.now()
    alert["handleNote"] = received["handleNote"]
    alert.save()

    if Alert.objects(node=node, isHandled=False).first() is None:
        node["state"] = update_state(
            node["state"], node["lastSeenAt"], PayloadType.HANDLE_ALERT
        )
        node.save()

    return alert

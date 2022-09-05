from datetime import datetime

from ..services.database import Alert, User
from .exceptions import ObjectNotFoundException
from .payload import PayloadType
from .sensor import update_state


def handle_alert(received: dict, user_id: str):
    alert = Alert.objects(id=received["alertID"]).first()

    if alert is None:
        raise ObjectNotFoundException(Alert)

    sensor = alert["sensor"]
    user = User.objects(id=user_id).first()

    alert["isConfirmed"] = received["isConfirmed"]
    alert["isHandled"] = True
    alert["handledBy"] = user
    alert["handledAt"] = datetime.now()
    alert["handleNote"] = received["handleNote"]
    alert.save()

    if Alert.objects(sensor=sensor, isHandled=False).first() is None:
        sensor["state"] = update_state(
            sensor["state"], sensor["lastSeenAt"], PayloadType.HANDLE_ALERT
        )
        sensor.save()

    return alert

from datetime import datetime
from typing import Union

from services.database import Alert, User

from utils.payload import PayloadType
from utils.sensor import update_state


def handle_alert(received: dict, user_id: str) -> Union[Alert, None]:
    alert = Alert.objects(id=received["alertID"]).first()

    if alert is None:
        return None

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

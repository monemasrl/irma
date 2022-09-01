import os
from datetime import datetime, timedelta

from services.database import Sensor

from utils.enums import PayloadType, SensorState

# valore teorico della soglia di pericolo del sensore
# TODO: move to config file
MAX_TRESHOLD = int(os.environ.get("MAX_TRESHOLD", 20))

# for sensor timeout
# TODO: move to config file
SENSORS_TIMEOUT_INTERVAL = timedelta(seconds=30)


def update_state_reading_alert(current_state: SensorState) -> SensorState:
    if current_state == SensorState.READY:
        return SensorState.ALERT_READY
    elif current_state == SensorState.RUNNING:
        return SensorState.ALERT_RUNNING

    return current_state


def update_state_start_rec(current_state: SensorState) -> SensorState:
    if current_state == SensorState.READY:
        return SensorState.RUNNING

    return current_state


def update_state_end_rec(current_state: SensorState) -> SensorState:
    if current_state == SensorState.RUNNING:
        return SensorState.READY
    elif current_state == SensorState.ALERT_RUNNING:
        return SensorState.ALERT_READY

    return current_state


def update_state_keep_alive(current_state: SensorState) -> SensorState:
    if current_state == SensorState.ERROR:
        return SensorState.READY

    return current_state


def update_state_handle_alert(current_state: SensorState) -> SensorState:
    if current_state == SensorState.ALERT_READY:
        return SensorState.READY
    elif current_state == SensorState.ALERT_RUNNING:
        return SensorState.RUNNING

    return current_state


def update_state(
    current_state: SensorState,
    lastSeenAt: datetime,
    typ: PayloadType | None = None,
    dato: int = 0,
) -> SensorState:

    if typ == PayloadType.READING and dato >= MAX_TRESHOLD:
        current_state = update_state_reading_alert(current_state)
    elif typ == PayloadType.START_REC:
        current_state = update_state_start_rec(current_state)
    elif typ == PayloadType.END_REC:
        current_state = update_state_end_rec(current_state)
    elif typ == PayloadType.KEEP_ALIVE:
        current_state = update_state_keep_alive(current_state)
    elif typ == PayloadType.HANDLE_ALERT:
        current_state = update_state_handle_alert(current_state)

    if (datetime.now() - lastSeenAt) > SENSORS_TIMEOUT_INTERVAL:
        current_state = SensorState.ERROR

    return current_state


def get_sensors(applicationID: str):
    return Sensor.objects(application=applicationID)

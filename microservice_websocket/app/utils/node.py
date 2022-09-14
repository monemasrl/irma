import os
from datetime import datetime, timedelta

from ..services.database import Node
from .enums import NodeState, PayloadType
from .exceptions import ObjectNotFoundException

# valore teorico della soglia di pericolo del sensore
# TODO: move to config file
MAX_TRESHOLD = int(os.environ.get("MAX_TRESHOLD", 20))

# for sensor timeout
# TODO: move to config file
SENSORS_TIMEOUT_INTERVAL = timedelta(seconds=30)


def update_state_total_reading(current_state: NodeState, dato: int) -> NodeState:
    if current_state == NodeState.READY:
        current_state = NodeState.RUNNING
    elif current_state == NodeState.ALERT_READY:
        current_state = NodeState.ALERT_RUNNING

    if dato >= MAX_TRESHOLD and current_state == NodeState.RUNNING:
        return NodeState.ALERT_RUNNING

    return current_state


def update_state_window_reading(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.READY:
        current_state = NodeState.RUNNING
    elif current_state == NodeState.ALERT_READY:
        current_state = NodeState.ALERT_RUNNING

    return current_state


def update_state_start_rec(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.READY:
        return NodeState.RUNNING

    return current_state


def update_state_end_rec(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.RUNNING:
        return NodeState.READY
    elif current_state == NodeState.ALERT_RUNNING:
        return NodeState.ALERT_READY

    return current_state


def update_state_keep_alive(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.ERROR:
        return NodeState.READY

    return current_state


def update_state_handle_alert(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.ALERT_READY:
        return NodeState.READY
    elif current_state == NodeState.ALERT_RUNNING:
        return NodeState.RUNNING

    return current_state


def update_state(
    current_state: NodeState,
    lastSeenAt: datetime,
    typ: PayloadType | None = None,
    dato: int = 0,
) -> NodeState:

    FUNCTIONS = {
        PayloadType.TOTAL_READING: update_state_total_reading,
        PayloadType.WINDOW_READING: update_state_window_reading,
        PayloadType.START_REC: update_state_start_rec,
        PayloadType.END_REC: update_state_end_rec,
        PayloadType.KEEP_ALIVE: update_state_keep_alive,
        PayloadType.HANDLE_ALERT: update_state_handle_alert,
    }

    if typ is not None:
        current_state = FUNCTIONS[typ](current_state, dato)

    if (datetime.now() - lastSeenAt) > SENSORS_TIMEOUT_INTERVAL:
        current_state = NodeState.ERROR

    return current_state


def get_nodes(applicationID: str):
    nodes = Node.objects(application=applicationID)

    if len(nodes) == 0:
        raise ObjectNotFoundException(Node)

    nodes = [x.to_dashboard() for x in nodes]

    return nodes

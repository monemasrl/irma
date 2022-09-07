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


def update_state_reading_alert(current_state: NodeState) -> NodeState:
    if current_state == NodeState.READY:
        return NodeState.ALERT_READY
    elif current_state == NodeState.RUNNING:
        return NodeState.ALERT_RUNNING

    return current_state


def update_state_start_rec(current_state: NodeState) -> NodeState:
    if current_state == NodeState.READY:
        return NodeState.RUNNING

    return current_state


def update_state_end_rec(current_state: NodeState) -> NodeState:
    if current_state == NodeState.RUNNING:
        return NodeState.READY
    elif current_state == NodeState.ALERT_RUNNING:
        return NodeState.ALERT_READY

    return current_state


def update_state_keep_alive(current_state: NodeState) -> NodeState:
    if current_state == NodeState.ERROR:
        return NodeState.READY

    return current_state


def update_state_handle_alert(current_state: NodeState) -> NodeState:
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
        current_state = NodeState.ERROR

    return current_state


def get_nodes(applicationID: str):
    nodes = Node.objects(application=applicationID)

    if len(nodes) == 0:
        raise ObjectNotFoundException(Node)

    return nodes

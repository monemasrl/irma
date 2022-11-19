from datetime import datetime, timedelta

from ..config import config
from ..services.database import Node
from .enums import NodeState, PayloadType
from .exceptions import ObjectNotFoundException


def update_state_total_reading(current_state: NodeState, dato: int) -> NodeState:
    if current_state == NodeState.ERROR:
        current_state = NodeState.READY

    if dato >= config["ALERT_TRESHOLD"] and current_state == NodeState.READY:
        return NodeState.ALERT_READY

    return current_state


def update_state_window_reading(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.READY or current_state == NodeState.ERROR:
        current_state = NodeState.RUNNING
    elif current_state == NodeState.ALERT_READY:
        current_state = NodeState.ALERT_RUNNING

    return current_state


def update_state_start_rec(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.READY or current_state == NodeState.ERROR:
        return NodeState.RUNNING

    return current_state


def update_state_end_rec(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.RUNNING or current_state == NodeState.ERROR:
        return NodeState.READY
    elif current_state == NodeState.ALERT_RUNNING:
        return NodeState.ALERT_READY

    return current_state


def update_state_keep_alive(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.ERROR:
        return NodeState.READY

    return current_state


def update_state_handle_alert(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.ALERT_READY or current_state == NodeState.ERROR:
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

    if (datetime.now() - lastSeenAt) > timedelta(
        seconds=config["NODE_TIMEOUT_INTERVAL"]
    ):
        current_state = NodeState.ERROR

    return current_state


def get_nodes(applicationID: str):
    nodes = Node.objects(application=applicationID)

    if len(nodes) == 0:
        raise ObjectNotFoundException(Node)

    nodes = [x.to_dashboard() for x in nodes]

    return nodes

from datetime import datetime

from backend.app.config import config
from backend.app.utils.enums import EventType, NodeState
from backend.app.utils.node import update_state

ALERT_TRESHOLD = config.app.ALERT_TRESHOLD


def case(
    current: NodeState,
    lastSeenAt: datetime,
    event: EventType | None,
    expected: NodeState,
):

    assert (
        got := update_state(current, lastSeenAt, event)
    ) == expected, f"Error from state '{current}' with timedelta \
    '{datetime.now() - lastSeenAt}' and event '{event}'. \
    Expected {expected} but got {got}"


def test_get_state():
    # fmt: off

    # From error
    case(NodeState.ERROR, datetime.now(), EventType.START_REC, NodeState.RUNNING)
    case(NodeState.ERROR, datetime.now(), EventType.STOP_REC, NodeState.READY)
    case(NodeState.ERROR, datetime.now(), EventType.RAISE_ALERT, NodeState.ALERT_READY)
    case(NodeState.ERROR, datetime.now(), EventType.HANDLE_ALERT, NodeState.READY)
    case(NodeState.ERROR, datetime.now(), EventType.KEEP_ALIVE, NodeState.READY)
    case(NodeState.ERROR, datetime.now(), EventType.ON_LAUNCH, NodeState.READY)

    # From ready
    case(NodeState.READY, datetime.now(), EventType.START_REC, NodeState.RUNNING)
    case(NodeState.READY, datetime.now(), EventType.STOP_REC, NodeState.READY)
    case(NodeState.READY, datetime.now(), EventType.RAISE_ALERT, NodeState.ALERT_READY)
    case(NodeState.READY, datetime.now(), EventType.HANDLE_ALERT, NodeState.READY)
    case(NodeState.READY, datetime.now(), EventType.KEEP_ALIVE, NodeState.READY)
    case(NodeState.READY, datetime.now(), EventType.ON_LAUNCH, NodeState.READY)
    case(NodeState.READY, datetime(2020, 6, 1, 3, 2, 1), None, NodeState.ERROR)

    # From running
    case(NodeState.RUNNING, datetime.now(), EventType.START_REC, NodeState.RUNNING)
    case(NodeState.RUNNING, datetime.now(), EventType.STOP_REC, NodeState.READY)
    case(NodeState.RUNNING, datetime.now(), EventType.RAISE_ALERT, NodeState.ALERT_READY)
    case(NodeState.RUNNING, datetime.now(), EventType.HANDLE_ALERT, NodeState.READY)
    case(NodeState.RUNNING, datetime.now(), EventType.KEEP_ALIVE, NodeState.RUNNING)
    case(NodeState.RUNNING, datetime.now(), EventType.ON_LAUNCH, NodeState.READY)
    case(NodeState.RUNNING, datetime(2020, 6, 1, 3, 2, 1), None, NodeState.ERROR)

    # From alert_ready
    case(NodeState.ALERT_READY, datetime.now(), EventType.START_REC, NodeState.RUNNING)
    case(NodeState.ALERT_READY, datetime.now(), EventType.STOP_REC, NodeState.READY)
    case(NodeState.ALERT_READY, datetime.now(), EventType.RAISE_ALERT, NodeState.ALERT_READY)
    case(NodeState.ALERT_READY, datetime.now(), EventType.HANDLE_ALERT, NodeState.READY)
    case(NodeState.ALERT_READY, datetime.now(), EventType.KEEP_ALIVE, NodeState.ALERT_READY)
    case(NodeState.ALERT_READY, datetime.now(), EventType.ON_LAUNCH, NodeState.READY)
    case(NodeState.ALERT_READY, datetime(2020, 6, 1, 3, 2, 1), None, NodeState.ERROR)

    # fmt: on

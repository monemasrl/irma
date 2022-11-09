from datetime import datetime

from microservice_websocket.app.config import config
from microservice_websocket.app.utils.enums import NodeState, PayloadType
from microservice_websocket.app.utils.node import update_state

ALERT_TRESHOLD = config.app.ALERT_TRESHOLD


def _test_update_state_case(
    current: NodeState,
    lastSeenAt: datetime,
    typ: PayloadType,
    dato: int,
    expected: NodeState,
):

    assert (
        got := update_state(current, lastSeenAt, typ, dato)
    ) == expected, f"Error from state '{current}' with timedelta \
    '{datetime.now() - lastSeenAt}', typ '{typ}' and dato '{dato}'. \
    Expected {expected} but got {got}"


def test_get_state():
    # From error
    _test_update_state_case(
        NodeState.ERROR, datetime.now(), PayloadType.TOTAL_READING, 0, NodeState.RUNNING
    )
    _test_update_state_case(
        NodeState.ERROR,
        datetime.now(),
        PayloadType.TOTAL_READING,
        ALERT_TRESHOLD,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.ERROR,
        datetime.now(),
        PayloadType.WINDOW_READING,
        0,
        NodeState.RUNNING,
    )
    _test_update_state_case(
        NodeState.ERROR, datetime.now(), PayloadType.START_REC, 0, NodeState.RUNNING
    )
    _test_update_state_case(
        NodeState.ERROR, datetime.now(), PayloadType.END_REC, 0, NodeState.READY
    )
    _test_update_state_case(
        NodeState.ERROR, datetime.now(), PayloadType.KEEP_ALIVE, 0, NodeState.READY
    )
    _test_update_state_case(
        NodeState.ERROR,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        NodeState.READY,
    )

    # From ready
    _test_update_state_case(
        NodeState.READY, datetime.now(), PayloadType.TOTAL_READING, 0, NodeState.RUNNING
    )
    _test_update_state_case(
        NodeState.READY,
        datetime.now(),
        PayloadType.TOTAL_READING,
        ALERT_TRESHOLD,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.READY,
        datetime.now(),
        PayloadType.WINDOW_READING,
        0,
        NodeState.RUNNING,
    )
    _test_update_state_case(
        NodeState.READY, datetime.now(), PayloadType.START_REC, 0, NodeState.RUNNING
    )
    _test_update_state_case(
        NodeState.READY, datetime.now(), PayloadType.END_REC, 0, NodeState.READY
    )
    _test_update_state_case(
        NodeState.READY, datetime.now(), PayloadType.KEEP_ALIVE, 0, NodeState.READY
    )
    _test_update_state_case(
        NodeState.READY,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        NodeState.READY,
    )
    _test_update_state_case(
        NodeState.READY,
        datetime(2020, 6, 1, 3, 2, 1),
        PayloadType.HANDLE_ALERT,
        0,
        NodeState.ERROR,
    )

    # From running
    _test_update_state_case(
        NodeState.RUNNING,
        datetime.now(),
        PayloadType.TOTAL_READING,
        0,
        NodeState.RUNNING,
    )
    _test_update_state_case(
        NodeState.RUNNING,
        datetime.now(),
        PayloadType.TOTAL_READING,
        ALERT_TRESHOLD,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.RUNNING,
        datetime.now(),
        PayloadType.WINDOW_READING,
        0,
        NodeState.RUNNING,
    )
    _test_update_state_case(
        NodeState.RUNNING,
        datetime.now(),
        PayloadType.START_REC,
        0,
        NodeState.RUNNING,
    )
    _test_update_state_case(
        NodeState.RUNNING, datetime.now(), PayloadType.END_REC, 0, NodeState.READY
    )
    _test_update_state_case(
        NodeState.RUNNING,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        NodeState.RUNNING,
    )
    _test_update_state_case(
        NodeState.RUNNING,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        NodeState.RUNNING,
    )

    # From alert_ready
    _test_update_state_case(
        NodeState.ALERT_READY,
        datetime.now(),
        PayloadType.TOTAL_READING,
        0,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.ALERT_READY,
        datetime.now(),
        PayloadType.WINDOW_READING,
        0,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.ALERT_READY,
        datetime.now(),
        PayloadType.START_REC,
        0,
        NodeState.ALERT_READY,
    )
    _test_update_state_case(
        NodeState.ALERT_READY,
        datetime.now(),
        PayloadType.END_REC,
        0,
        NodeState.ALERT_READY,
    )
    _test_update_state_case(
        NodeState.ALERT_READY,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        NodeState.ALERT_READY,
    )
    _test_update_state_case(
        NodeState.ALERT_READY,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        NodeState.READY,
    )
    _test_update_state_case(
        NodeState.ALERT_READY,
        datetime(2020, 6, 1, 3, 2, 1),
        PayloadType.HANDLE_ALERT,
        0,
        NodeState.ERROR,
    )

    # From alert_running
    _test_update_state_case(
        NodeState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.TOTAL_READING,
        0,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.WINDOW_READING,
        0,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.START_REC,
        0,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.END_REC,
        0,
        NodeState.ALERT_READY,
    )
    _test_update_state_case(
        NodeState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        NodeState.ALERT_RUNNING,
    )
    _test_update_state_case(
        NodeState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        NodeState.RUNNING,
    )

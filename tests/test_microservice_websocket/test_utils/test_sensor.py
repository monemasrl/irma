from datetime import datetime

from microservice_websocket_docker.app.utils.enums import PayloadType, SensorState
from microservice_websocket_docker.app.utils.sensor import MAX_TRESHOLD, update_state


def _test_update_state_case(
    current: SensorState,
    lastSeenAt: datetime,
    typ: PayloadType,
    dato: int,
    expected: SensorState,
):

    assert (
        got := update_state(current, lastSeenAt, typ, dato)
    ) == expected, f"Error from state '{current}' with timedelta \
    '{datetime.now() - lastSeenAt}', typ '{typ}' and dato '{dato}'. \
    Expected {expected} but got {got}"


def test_get_state():
    # From error
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.READING, 0, SensorState.ERROR
    )
    _test_update_state_case(
        SensorState.ERROR,
        datetime.now(),
        PayloadType.READING,
        MAX_TRESHOLD,
        SensorState.ERROR,
    )
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.START_REC, 0, SensorState.ERROR
    )
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.END_REC, 0, SensorState.ERROR
    )
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.KEEP_ALIVE, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.ERROR,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.ERROR,
    )

    # From ready
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.READING, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.READY,
        datetime.now(),
        PayloadType.READING,
        MAX_TRESHOLD,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.START_REC, 0, SensorState.RUNNING
    )
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.END_REC, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.KEEP_ALIVE, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.READY,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.READY,
    )
    _test_update_state_case(
        SensorState.READY,
        datetime(2020, 6, 1, 3, 2, 1),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.ERROR,
    )

    # From running
    _test_update_state_case(
        SensorState.RUNNING, datetime.now(), PayloadType.READING, 0, SensorState.RUNNING
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.READING,
        MAX_TRESHOLD,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.START_REC,
        0,
        SensorState.RUNNING,
    )
    _test_update_state_case(
        SensorState.RUNNING, datetime.now(), PayloadType.END_REC, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        SensorState.RUNNING,
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.RUNNING,
    )

    # From alert_ready
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.READING,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.START_REC,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.END_REC,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime(2020, 6, 1, 3, 2, 1),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.ERROR,
    )

    # From alert_running
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.READING,
        0,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.START_REC,
        0,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.END_REC,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.RUNNING,
    )

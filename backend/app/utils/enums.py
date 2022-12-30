from enum import IntEnum, auto


class NodeState(IntEnum):
    ERROR = 0
    READY = auto()
    RUNNING = auto()
    ALERT_READY = auto()
    ALERT_RUNNING = auto()

    @classmethod
    def to_irma_ui_state(cls, n: int) -> str:
        if n == 0:
            return "off"
        elif n == 1:
            return "ok"
        elif n == 2:
            return "rec"
        elif n == 3:
            return "alert-ready"
        elif n == 4:
            return "alert-running"
        else:
            raise ValueError


class CommandType(IntEnum):
    START_REC = 0
    STOP_REC = auto()
    SET_DEMO_1 = auto()
    SET_DEMO_2 = auto()


class EventType(IntEnum):
    START_REC = 0
    STOP_REC = auto()
    RAISE_ALERT = auto()
    HANDLE_ALERT = auto()
    KEEP_ALIVE = auto()
    ON_LAUNCH = auto()
    TIMEOUT = auto()

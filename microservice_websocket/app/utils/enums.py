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


class PayloadType(IntEnum):
    TOTAL_READING = 0
    WINDOW_READING = auto()
    START_REC = auto()
    END_REC = auto()
    KEEP_ALIVE = auto()
    HANDLE_ALERT = auto()

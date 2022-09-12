from enum import IntEnum, auto
from typing import TypedDict

from can import Message


class Sipm(IntEnum):
    S1 = 0b00000000
    S2 = 0b10000000

    def __int__(self) -> int:
        CONVERSION = {Sipm.S1: 1, Sipm.S2: 2}
        return CONVERSION[self]


class Window(IntEnum):
    W1 = 0b00000001
    W2 = 0b00000010
    W3 = 0b00000011

    def __int__(self) -> int:
        CONVERSION = {
            Window.W1: 1,
            Window.W2: 2,
            Window.W3: 3,
        }
        return CONVERSION[self]


WINDOW_LOW = 0b00000000
WINDOW_HIGH = 0b01000000


class MessageType(IntEnum):
    START_COUNT = 1
    STOP_COUNT = auto()
    GET_WINDOW = auto()
    GET_TOTAL_COUNT = auto()
    SET_WINDOW_LOW = auto()
    SET_WINDOW_HIGH = auto()
    SET_HV = auto()
    ENABLE_BOARD = auto()
    DISABLE_BOARD = auto()
    RETURN_COUNT_WINDOW = auto()
    RETURN_COUNT_TOTAL = auto()


class Detector(IntEnum):
    D1 = 1
    D2 = auto()
    D3 = auto()
    D4 = auto()
    BROADCAST = auto()

    def __int__(self) -> int:
        CONVERSION = {Detector.D1: 1, Detector.D2: 2, Detector.D3: 3, Detector.D4: 4}
        return CONVERSION[self]


class DecodedMessage(TypedDict):
    message_type: MessageType
    n_detector: int
    sipm: Sipm
    count: int
    value: int
    sessionID: int
    readingID: int


def start_count() -> Message:
    return Message(
        arbitration_id=Detector.BROADCAST,
        data=[0, 0, 0, 0, 0, 0, MessageType.START_COUNT, 0],
    )


def stop_count() -> Message:
    return Message(
        arbitration_id=Detector.BROADCAST,
        data=[0, 0, 0, 0, 0, 0, MessageType.STOP_COUNT, 0],
    )


def get_window(n_window: Window, sipm: Sipm) -> Message:
    byte0 = n_window | sipm

    return Message(
        arbitration_id=Detector.BROADCAST,
        data=[byte0, 0, 0, 0, 0, 0, MessageType.GET_WINDOW, 0],
    )


def get_total_count(sipm: Sipm) -> Message:
    return Message(
        arbitration_id=Detector.BROADCAST,
        data=[sipm, 0, 0, 0, 0, 0, MessageType.GET_TOTAL_COUNT, 0],
    )


def set_window_low(
    can_id: Detector, sipm: Sipm, n_window: Window, value: int
) -> Message:
    if can_id == Detector.BROADCAST:
        raise ValueError("Cannot send 'SET WINDOW LOW' as BROADCAST")

    value.to_bytes(2, "big")

    byte0 = n_window | sipm | WINDOW_LOW

    return Message(
        arbitration_id=can_id,
        data=[byte0, 0, 0, 0, value[0], value[1], MessageType.SET_WINDOW_LOW, 0],
    )


def set_window_high(
    can_id: Detector, sipm: Sipm, n_window: Window, value: int
) -> Message:
    if can_id == Detector.BROADCAST:
        raise ValueError("Cannot send 'SET WINDOW HIGH' as BROADCAST")

    value.to_bytes(2, "big")

    byte0 = n_window | sipm | WINDOW_HIGH

    return Message(
        arbitration_id=can_id,
        data=[byte0, 0, 0, 0, value[0], value[1], MessageType.SET_WINDOW_HIGH, 0],
    )


def set_hv(can_id: Detector, sipm: Sipm, value: int) -> Message:
    if can_id == Detector.BROADCAST:
        raise ValueError("Cannot send 'SET HV' as BROADCAST")

    value.to_bytes(2, "big")

    return Message(
        arbitration_id=can_id,
        data=[sipm, 0, 0, 0, value[0], value[1], MessageType.SET_HV, 0],
    )


def enable_board(can_id: Detector) -> Message:
    if can_id == Detector.BROADCAST:
        raise ValueError("Cannot send 'ENABLE BOARD' as BROADCAST")

    return Message(
        arbitration_id=can_id,
        data=[0, 0, 0, 0, 0, 0, MessageType.ENABLE_BOARD, 0],
    )


def disable_board(can_id: Detector) -> Message:
    if can_id == Detector.BROADCAST:
        raise ValueError("Cannot send 'DISABLE BOARD' as BROADCAST")

    return Message(
        arbitration_id=can_id,
        data=[0, 0, 0, 0, 0, 0, MessageType.DISABLE_BOARD, 0],
    )


def decode(message: Message, sessionID: int, readingID: int) -> DecodedMessage:
    data = message.data

    n_detector = data[7]

    if data[6] == MessageType.RETURN_COUNT_WINDOW:
        count = int.from_bytes(data[3:6], "big")
        n_window = data[0] & 0b00111111
        sipm = data[0] >> 7
        return {
            "message_type": MessageType.RETURN_COUNT_WINDOW,
            "n_detector": n_detector,
            "sipm": int(Sipm.S1 if sipm == 0 else Sipm.S2),
            "value": n_window,
            "count": count,
            "sessionID": sessionID,
            "readingID": readingID,
        }

    elif data[6] == MessageType.RETURN_COUNT_TOTAL:
        count = int.from_bytes(data[3:6], "big")
        danger_level = data[2]
        sipm = data[0] >> 7
        return {
            "message_type": MessageType.RETURN_COUNT_TOTAL,
            "n_detector": n_detector,
            "sipm": int(Sipm.S1 if sipm == 0 else Sipm.S2),
            "value": danger_level,
            "count": count,
            "sessionID": sessionID,
            "readingID": readingID,
        }
    else:
        raise ValueError(f"Unexpected MessageType '{data[6]}'")

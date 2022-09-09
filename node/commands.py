from enum import IntEnum, auto
from typing import Optional, TypedDict

from can import BufferedReader, CyclicSendTaskABC, Message
from can.interface import Bus


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
    n_detector: int
    message_type: MessageType
    sipm: Sipm
    count: int
    n_window: Optional[int]
    danger_level: Optional[int]


class IrmaBus(Bus):
    def __init__(self, bustype, channel, bitrate, period=10):
        super().__init__(bustype=bustype, channel=channel, bitrate=bitrate)
        # TODO: ????????
        self.listener = BufferedReader()
        self.period = period
        self.cyclic_send = None

    def listen(self, timeout=0.5) -> Optional[dict]:
        message = self.listener.get_message(timeout)

        if message is None:
            return None

        return decode_message(message)

    def send_start_count(self):
        message = Message(
            arbitration_id=Detector.BROADCAST,
            data=[0, 0, 0, 0, 0, 0, MessageType.START_COUNT, 0],
        )
        self.send(message)
        self.cyclic_send: CyclicSendTaskABC = self.send_periodic(
            self.get_total_count_message(), 10
        )

    def send_stop_count(self):
        message = Message(
            arbitration_id=Detector.BROADCAST,
            data=[0, 0, 0, 0, 0, 0, MessageType.STOP_COUNT, 0],
        )
        self.send(message)
        if self.cyclic_send is not None:
            self.cyclic_send.stop()

    def get_window(self, n_window: Window, sipm: Sipm):
        byte0 = n_window | sipm

        message = Message(
            arbitration_id=Detector.BROADCAST,
            data=[byte0, 0, 0, 0, 0, 0, MessageType.GET_WINDOW, 0],
        )
        self.send(message)

    def get_total_count_message(self, sipm: Sipm):
        return Message(
            arbitration_id=Detector.BROADCAST,
            data=[sipm, 0, 0, 0, 0, 0, MessageType.GET_TOTAL_COUNT, 0],
        )

    def set_window_low(self, id: Detector, sipm: Sipm, n_window: Window, value: int):
        if id == Detector.BROADCAST:
            raise ValueError("Cannot send 'SET WINDOW LOW' as BROADCAST")

        value.to_bytes(2, "big")

        byte0 = n_window | sipm | WINDOW_LOW

        message = Message(
            arbitration_id=id,
            data=[byte0, 0, 0, 0, value[0], value[1], MessageType.SET_WINDOW_LOW, 0],
        )
        self.send(message)

    def set_window_high(self, id: Detector, sipm: Sipm, n_window: Window, value: int):
        if id == Detector.BROADCAST:
            raise ValueError("Cannot send 'SET WINDOW HIGH' as BROADCAST")

        value.to_bytes(2, "big")

        byte0 = n_window | sipm | WINDOW_HIGH

        message = Message(
            arbitration_id=id,
            data=[byte0, 0, 0, 0, value[0], value[1], MessageType.SET_WINDOW_HIGH, 0],
        )
        self.send(message)

    def set_hv(self, id: Detector, sipm: Sipm, value: int):
        if id == Detector.BROADCAST:
            raise ValueError("Cannot send 'SET HV' as BROADCAST")

        value.to_bytes(2, "big")

        message = Message(
            arbitration_id=id,
            data=[sipm, 0, 0, 0, value[0], value[1], MessageType.SET_HV, 0],
        )
        self.send(message)

    def enable_board(self, id: Detector):
        if id == Detector.BROADCAST:
            raise ValueError("Cannot send 'ENABLE BOARD' as BROADCAST")

        message = Message(
            arbitration_id=id,
            data=[0, 0, 0, 0, 0, 0, MessageType.ENABLE_BOARD, 0],
        )
        self.send(message)

    def disable_board(self, id: Detector):
        if id == Detector.BROADCAST:
            raise ValueError("Cannot send 'DISABLE BOARD' as BROADCAST")

        message = Message(
            arbitration_id=id,
            data=[0, 0, 0, 0, 0, 0, MessageType.DISABLE_BOARD, 0],
        )
        self.send(message)


def decode_message(message: Message) -> DecodedMessage:
    data = message.data

    n_detector = data[7]

    if data[6] == MessageType.RETURN_COUNT_WINDOW:
        count = int.from_bytes(data[3:6], "big")
        n_window = data[0] & 0b00111111
        sipm = data[0] >> 7
        return {
            "n_detector": n_detector,
            "message_type": MessageType.RETURN_COUNT_WINDOW,
            "n_window": n_window,
            "sipm": Sipm.S1 if sipm == 0 else Sipm.S2,
            "count": count,
        }

    elif data[6] == MessageType.RETURN_COUNT_TOTAL:
        count = int.from_bytes(data[3:6], "big")
        danger_level = data[2]
        sipm = data[0] >> 7
        return {
            "n_detector": n_detector,
            "message_type": MessageType.RETURN_COUNT_TOTAL,
            "sipm": Sipm.S1 if sipm == 0 else Sipm.S2,
            "danger_level": danger_level,
            "count": count,
        }
    else:
        raise ValueError(f"Unexpected MessageType '{data[6]}'")

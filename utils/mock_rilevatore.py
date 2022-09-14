from enum import IntEnum, auto
from typing import Optional

from can import Message
from can.interface import Bus


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


class RilevatoreBus:
    def __init__(self, bustype, channel, bitrate, detector: Detector):
        self._bus = Bus(bustype=bustype, channel=channel, bitrate=bitrate)
        self.detector = detector

    def send(self, message: Message, timeout: Optional[float] = None):
        self._bus.send(message, timeout)

    def start_count(self, msg):
        print("Received START COUNT!")

    def stop_count(self, msg):
        print("Recevied STOP COUNT!")

    def get_window(self, msg: Message):
        print("Received GET WINDOW!")
        byte0 = msg.data[0]
        sipm = 1 if byte0 >> 7 == 0 else 2
        window = byte0 & 0b00111111

        print(f"SIPM: {sipm}")
        print(f"Window: {window}")

        reading = int(input("Inserisci valore per la finestra: "))
        encoded_reading = reading.to_bytes(3, "big")

        new_msg = Message(
            arbitration_id=0,
            data=[
                byte0,
                0,
                0,
                encoded_reading[0],
                encoded_reading[1],
                encoded_reading[2],
                MessageType.RETURN_COUNT_WINDOW,
                self.detector,
            ],
        )
        self.send(new_msg)
        print("Sent RETURN COUNT WINDOW!")

    def get_total_count(self, msg: Message):
        print("Received GET TOTAL COUNT!")
        byte0 = msg.data[0]
        sipm = 1 if byte0 >> 7 == 0 else 2

        print(f"SIPM: {sipm}")

        count = int(input("Inserisci il conteggio: "))
        encoded_count = count.to_bytes(3, "big")
        danger_level = int(input("Inserisci il livello di pericolosita: "))

        new_msg = Message(
            arbitration_id=0,
            data=[
                byte0,
                0,
                danger_level,
                encoded_count[0],
                encoded_count[1],
                encoded_count[2],
                MessageType.RETURN_COUNT_TOTAL,
                self.detector,
            ],
        )
        self.send(new_msg)
        print("Sent RETURN COUNT TOTAL!")

    def set_window_low(self, msg: Message):
        print("Received SET WINDOW LOW!")
        byte0 = msg.data[0]
        sipm = 1 if byte0 >> 7 == 0 else 2
        window = byte0 & 0b00111111
        value = int.from_bytes(msg.data[4:6], "big")

        print(f"SIPM: {sipm}")
        print(f"Window: {window}")
        print(f"Settaggio: {value}")

    def set_window_high(self, msg: Message):
        print("Received SET WINDOW HIGH!")
        byte0 = msg.data[0]
        sipm = 1 if byte0 >> 7 == 0 else 2
        window = byte0 & 0b00111111
        value = int.from_bytes(msg.data[4:6], "big")

        print(f"SIPM: {sipm}")
        print(f"Window: {window}")
        print(f"Settaggio: {value}")

    def set_hv(self, msg):
        print("Received SET HV!")
        byte0 = msg.data[0]
        sipm = 1 if byte0 >> 7 == 0 else 2
        value = int.from_bytes(msg.data[4:6], "big")

        print(f"SIPM: {sipm}")
        print(f"Settaggio: {value}")

    def enable_board(self, msg):
        print("Received ENABLE BOARD!")

    def disable_board(self, msg):
        print("Received DISABLE BOARD!")

    def unknown(self, msg):
        print("Received unexpected payload")

    def decode(self, msg: Message):
        print("------------------")
        if msg.arbitration_id not in [self.detector, Detector.BROADCAST]:
            print(f"Discarding message with ID: {msg.arbitration_id}")
            return

        cases = {
            MessageType.START_COUNT: self.start_count,
            MessageType.STOP_COUNT: self.stop_count,
            MessageType.GET_WINDOW: self.get_window,
            MessageType.GET_TOTAL_COUNT: self.get_total_count,
            MessageType.SET_WINDOW_LOW: self.set_window_low,
            MessageType.SET_WINDOW_HIGH: self.set_window_high,
            MessageType.SET_HV: self.set_hv,
            MessageType.ENABLE_BOARD: self.enable_board,
            MessageType.DISABLE_BOARD: self.disable_board,
            MessageType.RETURN_COUNT_WINDOW: self.unknown,
            MessageType.RETURN_COUNT_TOTAL: self.unknown,
        }

        data = msg.data
        cases[data[6]](msg)
        print("------------------")

    def loop_forever(self):
        while True:
            msg = self._bus.recv()
            if msg is None:
                continue
            self.decode(msg)


if __name__ == "__main__":
    bus = RilevatoreBus(
        bustype="socketcan", channel="can0", bitrate=12500, detector=Detector.D1
    )
    bus.loop_forever()

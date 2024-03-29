import time
from threading import Lock
from time import sleep
from typing import Optional

import can_protocol
from apscheduler.schedulers.background import BackgroundScheduler
from can.interface import Bus
from can.message import Message


class IrmaBus:
    def __init__(
        self,
        bustype,
        channel,
        bitrate,
        interval_seconds=30,
        filter_id: Optional[int] = None,
        filter_mask: Optional[int] = None,
    ):
        self._bus = Bus(bustype=bustype, channel=channel, bitrate=bitrate)
        if filter_id and filter_mask:
            self._bus.set_filters(
                # [{"can_id": 0b01100000, "can_mask": 0b11111000, "extended": False}]
                [{"can_id": filter_id, "can_mask": filter_mask, "extended": False}]
            )
        self._sessionID = None
        self._readingID = None
        self._scheduler = BackgroundScheduler()
        self._lock = Lock()

        self._scheduler.add_job(self.loop, "interval", seconds=interval_seconds)
        self._scheduler.start(paused=True)

    def loop(self):
        sleep(5)

        with self._lock:
            self._readingID = int(time.time())

        # Richiesta finestra1
        self.send(can_protocol.get_window(can_protocol.Window.W1, can_protocol.Sipm.S1))
        sleep(0.5)
        self.send(can_protocol.get_window(can_protocol.Window.W1, can_protocol.Sipm.S2))
        sleep(0.5)

        # Richiesta finestra2
        self.send(can_protocol.get_window(can_protocol.Window.W2, can_protocol.Sipm.S1))
        sleep(0.5)
        self.send(can_protocol.get_window(can_protocol.Window.W2, can_protocol.Sipm.S2))
        sleep(0.5)

        # Richiesta finestra3
        self.send(can_protocol.get_window(can_protocol.Window.W3, can_protocol.Sipm.S1))
        sleep(0.5)
        self.send(can_protocol.get_window(can_protocol.Window.W3, can_protocol.Sipm.S2))
        sleep(0.5)

    def listen(self, timeout=0.5) -> Optional[can_protocol.DecodedMessage]:
        message = self._bus.recv(timeout)

        if self._sessionID is None:
            self._sessionID = int(time.time())

        if message is None:
            return None

        with self._lock:
            if self._readingID is None:
                self._readingID = int(time.time())
            readingID = self._readingID

        return can_protocol.decode(message, self._sessionID, readingID)

    def send(self, message: Message, timeout: Optional[float] = None):
        self._bus.send(message, timeout)

    def set_hv(self, detector: int, sipm: int, value: int):
        self.send(
            can_protocol.set_hv(
                can_protocol.Detector.parse_int(detector),
                can_protocol.Sipm.parse_int(sipm),
                value,
            )
        )

    def set_window_low(self, detector: int, sipm: int, window_number: int, value: int):
        self.send(
            can_protocol.set_window_low(
                can_protocol.Detector.parse_int(detector),
                can_protocol.Sipm.parse_int(sipm),
                can_protocol.Window.parse_int(window_number),
                value,
            )
        )

    def set_window_high(self, detector: int, sipm: int, window_number: int, value: int):
        self.send(
            can_protocol.set_window_high(
                can_protocol.Detector.parse_int(detector),
                can_protocol.Sipm.parse_int(sipm),
                can_protocol.Window.parse_int(window_number),
                value,
            )
        )

    def start_session(self, mode: int) -> int:
        self._sessionID = int(time.time())
        self.send(can_protocol.start_count(mode))
        # TODO: tweak
        time.sleep(0.5)
        self._scheduler.resume()

        return self._sessionID

    def stop_session(self):
        self._scheduler.pause()
        # TODO: tweak
        time.sleep(0.5)
        self.send(can_protocol.stop_count())
        time.sleep(0.2)
        self.send(can_protocol.get_total_count(can_protocol.Sipm.S1))
        sleep(0.5)
        self.send(can_protocol.get_total_count(can_protocol.Sipm.S2))
        sleep(0.5)

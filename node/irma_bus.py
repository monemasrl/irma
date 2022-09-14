import time
from threading import Lock
from typing import Optional

import can_protocol
from apscheduler.schedulers.background import BackgroundScheduler
from can import BufferedReader, Message
from can.interface import Bus


class IrmaBus:
    def __init__(self, bustype, channel, bitrate, interval_minutes=2):
        self._bus = Bus(bustype=bustype, channel=channel, bitrate=bitrate)
        # TODO: ????????
        self._listener = BufferedReader()
        self._sessionID = None
        self._readingID = None
        self._scheduler = BackgroundScheduler()
        self._lock = Lock()

        self._scheduler.add_job(self.loop, "interval", minutes=interval_minutes)

    def loop(self):
        with self._lock:
            self._readingID = int(time.time())

        # Richiesta total count ai sipm
        self.send(can_protocol.get_total_count(can_protocol.Sipm.S1))
        self.send(can_protocol.get_total_count(can_protocol.Sipm.S2))

        # Richiesta finestra1
        self.send(can_protocol.get_window(can_protocol.Window.W1, can_protocol.Sipm.S1))
        self.send(can_protocol.get_window(can_protocol.Window.W1, can_protocol.Sipm.S2))

        # Richiesta finestra2
        self.send(can_protocol.get_window(can_protocol.Window.W2, can_protocol.Sipm.S1))
        self.send(can_protocol.get_window(can_protocol.Window.W2, can_protocol.Sipm.S2))

        # Richiesta finestra3
        self.send(can_protocol.get_window(can_protocol.Window.W3, can_protocol.Sipm.S1))
        self.send(can_protocol.get_window(can_protocol.Window.W3, can_protocol.Sipm.S2))

    def listen(self, timeout=0.5) -> Optional[can_protocol.DecodedMessage]:
        message = self._listener.get_message(timeout)

        if message is None:
            return None

        with self._lock:
            readingID = self._readingID

        return can_protocol.decode(message, self._sessionID, readingID)

    def send(self, message: Message, timeout: Optional[float] = None):
        self._bus.send(message, timeout)

    def start_session(self):
        self._sessionID = int(time.time())
        self.send(can_protocol.start_count())
        # TODO: tweak
        time.sleep(0.5)
        self._scheduler.start()

    def stop_session(self):
        self._scheduler.stop()
        # TODO: tweak
        time.sleep(0.5)
        self.send(can_protocol.stop_count())

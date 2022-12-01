import time
from queue import Empty, Queue
from random import randint
from threading import Lock

import can_protocol
from apscheduler.schedulers.background import BackgroundScheduler
from can.message import Message
from can_protocol import Detector, Sipm, Window

x = {
    1: {
        1: 0,
        2: 0,
        3: 0,
    },
    2: {
        1: 0,
        2: 0,
        3: 0,
    },
    "dangerLevel": 0,
}


cache = [dict.copy(x) for _ in range(4)]


def init_cache():
    for detector in cache:
        detector[1][1] = 0
        detector[1][2] = 0
        detector[1][3] = 0
        detector[2][1] = 0
        detector[2][2] = 0
        detector[2][3] = 0
        detector["dangerLevel"] = randint(0, 9)


def gen_total_count(detector: Detector, sipm: Sipm) -> Message:
    count = 0
    for sensor in [1, 2]:
        for key in cache[detector - 1][sensor]:
            count += cache[detector - 1][sensor][key]

    encoded_count = count.to_bytes(3, "little")
    byte0 = sipm

    danger_level = cache[detector - 1]["dangerLevel"]

    return Message(
        arbitration_id=0,
        data=[
            byte0,
            0,
            danger_level,
            encoded_count[0],
            encoded_count[1],
            encoded_count[2],
            can_protocol.MessageType.RETURN_COUNT_TOTAL,
            detector,
        ],
    )


def gen_window_count(detector: Detector, window: Window, sipm: Sipm) -> Message:
    cache[detector - 1][int(sipm)][int(window)] += randint(0, 100)
    reading = cache[detector - 1][int(sipm)][int(window)]
    encoded_reading = reading.to_bytes(3, "little")
    byte0 = window | sipm

    return Message(
        arbitration_id=0,
        data=[
            byte0,
            0,
            0,
            encoded_reading[0],
            encoded_reading[1],
            encoded_reading[2],
            can_protocol.MessageType.RETURN_COUNT_WINDOW,
            detector,
        ],
    )


class MockBus:
    def __init__(self, interval_minutes=2):
        self._sessionID = None
        self._readingID = None
        self._scheduler = BackgroundScheduler()
        self._lock = Lock()

        self._scheduler.add_job(self.loop, "interval", minutes=interval_minutes)
        self._scheduler.start(paused=True)

        self._msgqueue: Queue = Queue()

    def loop(self):
        with self._lock:
            self._readingID = int(time.time())

        # Richiesta finestra1
        self._msgqueue.put(gen_window_count(Detector.D1, Window.W1, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D1, Window.W1, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D2, Window.W1, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D2, Window.W1, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D3, Window.W1, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D3, Window.W1, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D4, Window.W1, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D4, Window.W1, Sipm.S2))

        # Richiesta finestra2
        self._msgqueue.put(gen_window_count(Detector.D1, Window.W2, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D1, Window.W2, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D2, Window.W2, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D2, Window.W2, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D3, Window.W2, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D3, Window.W2, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D4, Window.W2, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D4, Window.W2, Sipm.S2))

        # Richiesta finestra3
        self._msgqueue.put(gen_window_count(Detector.D1, Window.W3, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D1, Window.W3, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D2, Window.W3, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D2, Window.W3, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D3, Window.W3, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D3, Window.W3, Sipm.S2))
        self._msgqueue.put(gen_window_count(Detector.D4, Window.W3, Sipm.S1))
        self._msgqueue.put(gen_window_count(Detector.D4, Window.W3, Sipm.S2))

    def listen(self, timeout=0.5) -> can_protocol.DecodedMessage | None:
        try:
            message = self._msgqueue.get(timeout=timeout)
        except Empty:
            message = None

        if message is None:
            return None

        with self._lock:
            readingID = self._readingID

        return can_protocol.decode(message, self._sessionID, readingID)

    def set_demo(self, version: 1 | 2):
        print("Received SET DEMO " + str(version))

    def start_session(self):
        self._sessionID = int(time.time())
        init_cache()
        # TODO: tweak
        time.sleep(0.5)
        self._scheduler.resume()
        self.loop()

    def stop_session(self):
        self._scheduler.pause()
        # TODO: tweak
        time.sleep(0.5)

        # Richiesta total count ai sipm
        self._msgqueue.put(gen_total_count(Detector.D1, Sipm.S1))
        self._msgqueue.put(gen_total_count(Detector.D1, Sipm.S2))
        self._msgqueue.put(gen_total_count(Detector.D2, Sipm.S1))
        self._msgqueue.put(gen_total_count(Detector.D2, Sipm.S2))
        self._msgqueue.put(gen_total_count(Detector.D3, Sipm.S1))
        self._msgqueue.put(gen_total_count(Detector.D3, Sipm.S2))
        self._msgqueue.put(gen_total_count(Detector.D4, Sipm.S1))
        self._msgqueue.put(gen_total_count(Detector.D4, Sipm.S2))

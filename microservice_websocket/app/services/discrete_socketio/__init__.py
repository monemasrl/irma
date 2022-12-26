from threading import Lock

from fastapi import FastAPI
from fastapi_socketio import SocketManager


class DiscreteSocketManager:
    def __init__(self, app: FastAPI):
        self._socket_manager = SocketManager(app=app, cors_allowed_origins=[])
        self._event_set: set[str] = set()
        self._lock = Lock()

    def emit(self, event: str):
        with self._lock:
            self._event_set.add(event)

    async def periodic_trigger(self):
        with self._lock:
            for event in self._event_set:
                print(f"[SocketIO] Emitting '{event}'")
                await self._socket_manager.emit(event)

            self._event_set.clear()

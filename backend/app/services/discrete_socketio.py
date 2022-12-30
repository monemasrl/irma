import logging
from threading import Lock
from typing import Literal

from fastapi import FastAPI
from fastapi_socketio import SocketManager

logger = logging.getLogger(__name__)


class FilterSocketIO(logging.Filter):
    def __init__(self, level: int):
        self.level = level

    def filter(self, record: logging.LogRecord):
        if any(
            s in record.getMessage()
            for s in [
                " /socket.io/?",
                "connection open",
                "connection close",
                '"WebSocket /socket.io/" [accepted]',
            ]
        ):
            if self.level > logging.DEBUG:
                return 0

            record.levelname = "DEBUG"
            record.levelno = 10

        return 1


logging.getLogger("uvicorn.access").addFilter(FilterSocketIO(logger.level))
logging.getLogger("uvicorn.error").addFilter(FilterSocketIO(logger.level))


class DiscreteSocketManager:
    def __init__(self, app: FastAPI):
        self._socket_manager = SocketManager(app=app, cors_allowed_origins=[])
        self._event_set: set[str] = set()
        self._lock = Lock()

    def emit(self, event: Literal["change-node", "change-reading", "change-settings"]):
        logger.debug(f"Queued '{event}'")
        with self._lock:
            self._event_set.add(event)

    async def periodic_trigger(self):
        with self._lock:
            for event in self._event_set:
                logger.info(f"Emitting '{event}'")
                await self._socket_manager.emit(event)

            self._event_set.clear()

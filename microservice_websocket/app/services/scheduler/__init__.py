from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ...config import config as Config
from .jobs import check_node_states, trigger_socketio


def init_scheduler():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_node_states,
        "interval",
        id="update_state",
        seconds=Config.app.NODE_TIMEOUT_CHECK_INTERVAL,
    )

    scheduler.add_job(
        trigger_socketio,
        "interval",
        id="trigger_socketio",
        seconds=Config.app.SOCKETIO_MIN_FIRE_INTERVAL,
    )

    scheduler.start()

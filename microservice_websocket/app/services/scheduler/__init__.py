import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ...config import config as Config
from ...utils.sync_cache import sync_cached


def init_scheduler():
    scheduler = AsyncIOScheduler()

    def periodically_get_route():
        requests.get("http://localhost:8000/api/check")

    scheduler.add_job(
        periodically_get_route,
        "interval",
        id="update_state",
        seconds=Config.app.NODE_TIMEOUT_CHECK_INTERVAL,
    )

    async def periodically_sync_cache():
        await sync_cached()

    scheduler.add_job(
        periodically_sync_cache,
        "interval",
        id="sync_cache",
        seconds=Config.app.CHECK_SYNC_READY,
    )

    scheduler.start()

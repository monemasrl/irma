import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ...config import config
from ...utils.sync_cache import sync_cached


def init_scheduler():
    scheduler = AsyncIOScheduler()

    @scheduler.task(
        "interval", id="update_state", seconds=config["NODE_TIMEOUT_CHECK_INTERVAL"]
    )
    def periodically_get_route():
        requests.get("http://localhost:5000/api/check")

    @scheduler.task("interval", id="sync_cache", seconds=config["CHECK_SYNC_READY"])
    async def periodically_sync_cache():
        await sync_cached()

    scheduler.start()

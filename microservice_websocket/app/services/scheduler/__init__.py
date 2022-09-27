from datetime import timedelta
from flask import Flask
from flask_apscheduler import APScheduler
import requests
from ...utils.sync_cache import sync_cached

# TODO: move to config file
SYNC_CACHE_INTERVAL = timedelta(seconds=30)


def init_scheduler(app: Flask, update_interval: int):
    scheduler = APScheduler()
    scheduler.init_app(app)

    @scheduler.task("interval", id="update_state", seconds=update_interval)
    def periodically_get_route():
        requests.get("http://localhost:5000/api/check")

    @scheduler.task(
        "interval", id="sync_cache", seconds=SYNC_CACHE_INTERVAL.total_seconds()
    )
    def periodically_sync_cache():
        sync_cached()

    scheduler.start()

from flask import Flask
from flask_apscheduler import APScheduler
import requests
from ...utils.sync_cache import sync_cached
from ...config import config


def init_scheduler(app: Flask):
    scheduler = APScheduler()
    scheduler.init_app(app)

    @scheduler.task(
        "interval", id="update_state", seconds=config["NODE_TIMEOUT_CHECK_INTERVAL"]
    )
    def periodically_get_route():
        requests.get("http://localhost:5000/api/check")

    @scheduler.task("interval", id="sync_cache", seconds=config["CHECK_SYNC_READY"])
    def periodically_sync_cache():
        sync_cached()

    scheduler.start()

from flask import Flask
from flask_apscheduler import APScheduler
import requests


def init_scheduler(app: Flask, update_interval: int):
    scheduler = APScheduler()
    scheduler.init_app(app)

    @scheduler.task("interval", id="update_state", seconds=update_interval)
    def periodically_get_route():
        app.logger.info(f"Periodic get every {update_interval} seconds!")
        requests.get("http://localhost:5000/api/check")

    scheduler.start()

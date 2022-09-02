import json
import os
from datetime import timedelta

from flask import Flask

# da togliere
from flask_cors import CORS
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

from .services.socketio import init_socketio
from .services.database import init_db
from .services.jwt import init_jwt
from .services.mqtt import create_mqtt
from .services.scheduler import init_scheduler


# interval for checking sensor timeout
SENSORS_UPDATE_INTERVAL = timedelta(seconds=10)

# for testing purposes
# TODO: move to config file
DISABLE_MQTT = False if os.environ.get("DISABLE_MQTT") != 1 else True


socketio = SocketIO(cors_allowed_origins="*")
mqtt = None


def create_app(debug=False):
    app = Flask(__name__)
    global mqtt

    app.config.from_file("../config/config.json", load=json.load)
    app.debug = debug

    init_scheduler(app, SENSORS_UPDATE_INTERVAL.total_seconds())
    init_jwt(app)
    init_db(app)
    CORS(app)

    if not DISABLE_MQTT:
        mqtt = create_mqtt(app)

    from .blueprints.api import bp

    app.register_blueprint(bp)
    socketio.init_app(app)

    init_socketio(socketio)

    return app

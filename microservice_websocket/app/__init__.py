import json

from fakeredis import FakeRedis
from flask import Flask

from flask_cors import CORS
from flask_redis import FlaskRedis
from flask_socketio import SocketIO

from .services.database import init_db
from .services.jwt import init_jwt
from .services.mqtt import create_mqtt
from .services.scheduler import init_scheduler
from .services.socketio import init_socketio

DISABLE_MQTT = False

socketio = SocketIO(cors_allowed_origins="*")
mqtt = None
redis_client = FlaskRedis()


def create_app(testing=False, debug=False):
    app = Flask(__name__)
    global mqtt
    global redis_client

    app.config.from_file("../config/config_server.json", load=json.load)
    if testing:
        app.config.from_file("../config/config_server_testing.json", load=json.load)
        redis_client = FlaskRedis.from_custom_provider(FakeRedis)
        print(f"{redis_client=}")

    app.debug = debug

    redis_client.init_app(app)
    init_scheduler(app)
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

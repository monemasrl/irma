# import json
#
# from fakeredis import FakeRedis
# from fastapi import FastAPI
# from flask import Flask
# from flask_cors import CORS
# from flask_redis import FlaskRedis
# from flask_socketio import SocketIO
#
# from .services.database import init_db
# from .services.jwt import init_jwt
# from .services.mqtt import create_mqtt
# from .services.scheduler import init_scheduler
# from .services.socketio import init_socketio

# def create_app(testing=False, debug=False):
#     app = Flask(__name__)
#     global mqtt
#     global redis_client
#
#     app.config.from_file("../config/config_server.json", load=json.load)
#     if testing:
#         app.config.from_file("../config/config_server_testing.json", load=json.load)
#         redis_client = FlaskRedis.from_custom_provider(FakeRedis)
#         print(f"{redis_client=}")
#
#     app.debug = debug
#
#     redis_client.init_app(app)
#     init_scheduler(app)
#     init_jwt(app)
#     init_db(app)
#     CORS(app)
#
#     if not DISABLE_MQTT:
#         mqtt = create_mqtt(app)
#
#     from .blueprints.api import bp
#
#     app.register_blueprint(bp)
#     socketio.init_app(app)
#
#     init_socketio(socketio)
#
#     return app

from fastapi import FastAPI
from redis import Redis
from socketio import Client as SocketIOClient

from .services.database import init_db, user_manager
from .services.mqtt import init_mqtt
from .services.scheduler import init_scheduler

# TODO: move to config
DISABLE_MQTT = True

socketio = SocketIOClient()
mqtt = None
# TODO: move to config
redis_client = Redis(host="lolcahost", port=6379)

app = FastAPI()

if not DISABLE_MQTT:
    # TODO: move to config
    mqtt = init_mqtt("localhost", 1883)


@app.on_event("startup")
async def app_init():
    await init_db("mongomock://localhost:27017/test", "test")
    await user_manager.create_user("foo@bar.com", "baz")
    init_scheduler()


from .blueprints.api import main_router

app.include_router(main_router)

from fakeredis import FakeStrictRedis
from fastapi import FastAPI
from redis import Redis
from socketio import Client as SocketIOClient

from .services.database import init_db, user_manager
from .services.mqtt import init_mqtt
from .services.scheduler import init_scheduler

socketio = SocketIOClient()
mqtt = None

app = FastAPI()


@app.on_event("startup")
async def app_init():
    global redis_client
    global mqtt

    init_scheduler()

    from .config import TESTING, config as Config

    if not TESTING:
        mqtt = init_mqtt("localhost", 1883)
        redis_client = Redis(host="localhost", port=6379)
        await init_db(Config.mongo.uri, Config.mongo.db)
    else:
        redis_client = FakeStrictRedis()
        await init_db("mongomock://localhost:27017/test", "test")

    await user_manager.create_user("foo@bar.com", "baz", role="admin")


from .blueprints.api import main_router

app.include_router(main_router)

import yaml
import os
import logging
import logging.config

# Logging configuration
#
# Needs to be done before importing stuff to configure
# top-level loggers.
script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
relpath = "/config/logging.yaml"

path = "/".join(path_list[:-2]) + relpath
with open(path, "r") as f:
    config = yaml.load(f, Loader=yaml.Loader)
logging.config.dictConfig(config)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .services.database import init_db, user_manager
from .services.discrete_socketio import DiscreteSocketManager
from .services.mqtt import init_mqtt
from .services.scheduler import init_scheduler

mqtt = None

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

socketManager = DiscreteSocketManager(app)

logger.debug(
    f"List all available loggers: %s",
    [logging.getLogger(name) for name in logging.root.manager.loggerDict],
)


@app.on_event("startup")
async def app_init():
    logger.debug("Fired 'startup' event")
    global redis_client
    global mqtt

    init_scheduler()

    from .config import TESTING, config as Config

    if not TESTING:
        logger.debug("Loading standard configuration")
        mqtt = init_mqtt(Config.mqtt)
        mqtt.init_app(app)
        await init_db(Config.mongo.uri, Config.mongo.db)
    else:
        logger.debug("Loading testing configuration")
        await init_db("mongomock://localhost:27017/test", "test")

    logger.debug("Creating default user")
    await user_manager.create_user("foo@bar.com", "baz", "John", "Doe", role="admin")


from .blueprints.api import main_router

app.include_router(main_router)

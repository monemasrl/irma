import os

import yaml
from pydantic import BaseModel
from yaml.loader import Loader

TESTING = os.environ.get("TESTING", False)


class AppConfig(BaseModel):
    READING_SYNC_WAIT: int
    CHECK_SYNC_READY: int
    NODE_TIMEOUT_CHECK_INTERVAL: int
    NODE_TIMEOUT_INTERVAL: int
    ALERT_TRESHOLD: int


class JwtConfig(BaseModel):
    secret_key: str
    access_token_expires_minutes: int = 10


class MQTTConfig(BaseModel):
    username: str
    password: str
    host: str = "localhost"
    port: int = 1883
    tls_enabled: bool = False
    tls_version: int = 1


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class MongoConfig(BaseModel):
    db: str
    uri: str = "mongodb://localhost:27017"


class Config(BaseModel):
    app: AppConfig
    jwt: JwtConfig
    mqtt: MQTTConfig
    redis: RedisConfig
    mongo: MongoConfig


script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
relpath = "/config/config.yaml"

path = "/".join(path_list[:-2]) + relpath

with open(path) as f:
    config: Config = Config.parse_obj(yaml.load(f, Loader=Loader)["config"])

from __future__ import annotations

import os

import yaml
from pydantic import BaseModel

_config: Config | None = None


class MqttConfig(BaseModel):
    url: str
    port: int
    tls: bool
    user: str
    password: str


class Config(BaseModel):
    mobius_uri: str
    mqtt: MqttConfig

    @staticmethod
    def _load() -> Config:
        script_path = os.path.abspath(__file__)
        path_list = script_path.split(os.sep)
        relpath = "/config.yaml"

        path = "/".join(path_list[:-1]) + relpath
        with open(path) as f:
            return Config.parse_obj(yaml.load(f, Loader=yaml.Loader))


def get_config() -> Config:
    global _config

    if _config is None:
        _config = Config._load()
        return _config

    return _config

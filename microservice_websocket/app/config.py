import json
import os
from typing import TypedDict


class Config(TypedDict):
    READING_SYNC_WAIT: int
    NODE_STATUS_CHECK_INTERVAL: int
    NODE_TIMEOUT_INTERVAL: int
    ALERT_TRESHOLD: int
    CHECK_SYNC_READY: int


config: Config = {}

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
relpath = "/config/config.json"

path = "/".join(path_list[:-2]) + relpath

with open(path) as f:
    config = json.load(f)

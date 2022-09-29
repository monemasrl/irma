import json
import os
from typing import TypedDict


class ConversionEntry(TypedDict):
    sensorId: str
    sensorPath: str


class MobiusConfig:
    config = {}
    host: str
    port: int
    # Converts nodeID to sensorId and sensorPath
    conversion: dict[str, ConversionEntry]

    def __init__(self):
        script_path = os.path.abspath(__file__)
        path_list = script_path.split(os.sep)
        relpath = "/config/config_mobius.json"

        path = "/".join(path_list[:-4]) + relpath
        with open(path) as f:
            self.config = json.load(f)

    @property
    def host(self) -> str:
        return self.config["host"]

    @property
    def port(self) -> int:
        return self.config["port"]

    def nodeID_to_sensorId(self, nodeID: int) -> str:
        return self.config["conversion"][str(nodeID)]["sensorId"]

    def nodeID_to_sensorPath(self, nodeID: int) -> str:
        return self.config["conversion"][str(nodeID)]["sensorPath"]


config = MobiusConfig()

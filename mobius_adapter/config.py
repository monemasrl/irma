import json
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
        with open("./config.json") as f:
            self.config = json.load(f)

    @property
    def host(self) -> str:
        return self.config["host"]

    @property
    def port(self) -> int:
        return self.config["port"]

    @property
    def originator(self) -> str:
        return self.config["originator"]

    def nodeID_to_sensorId(self, nodeID: int) -> str:
        return self.config["conversion"][str(nodeID)]["sensorId"]

    def nodeID_to_sensorPath(self, nodeID: int) -> str:
        return self.config["conversion"][str(nodeID)]["sensorPath"]


config = MobiusConfig()

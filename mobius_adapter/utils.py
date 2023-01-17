from datetime import datetime

import requests
from pydantic import BaseModel

from config import get_config

config = get_config()


class Data(BaseModel):
    payloadType: str

    nodeID: int
    canID: int
    sensorNumber: int

    sessionID: int
    readingID: int

    value: int


def timestamp_millis() -> int:
    return int(datetime.now().timestamp() * 1000)


def insert(data: Data):
    requests.post(
        f"{config.mobius_uri}/{data.sessionID}",
        headers={
            "X-M2M-Origin": "MONEMA",
            "Content-Type": "application/json;ty=4",
            "X-M2M-RI": str(timestamp_millis()),
        },
        json={
            "m2m:cin": {
                "con": {
                    "metadata": {
                        "sensorId": data.sessionID,
                        "readingTimestamp": data.readingID,
                    },
                    "sensorData": data.json(),
                    "cnf": "application/json:0",
                }
            }
        },
    )


def create_session_container(sessionID: int):
    requests.post(
        config.mobius_uri,
        headers={
            "Content-Type": "application/json;ty=3",
            "X-M2M-RI": str(timestamp_millis()),
            "X-M2M-Origin": "MONEMA",
        },
        json={"m2m:cnt": {"rn": str(sessionID)}},
    )

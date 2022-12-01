from datetime import datetime

import requests
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from config import config


class Reading(BaseModel):
    id: PydanticObjectId
    node: PydanticObjectId
    canID: int = Field(default=..., lt=5, gt=0)
    sensorNumber: int = Field(default=..., lt=3, gt=0)
    readingID: int
    sessionID: int
    dangerLevel: int = 0
    window1: int = 0
    window2: int = 0
    window3: int = 0
    publishedAt: datetime


# Conversione reading per mobius
def to_mobius_payload(reading: Reading, sensorId: str) -> dict:
    return {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": sensorId,
                    "readingTimestamp": datetime.fromtimestamp(
                        reading.readingID
                    ).isoformat(),
                    # "latitude": <latitudine del sensore>, // opzionale
                    # "longitude": <longitudine del sensore>, // opzionale
                    # "heading": <orientazione del sensore>, // opzionale
                }
            },
            "sensorData": {
                "canID": reading.canID,
                "sensorNumber": reading.sensorNumber,
                "dangerLevel": reading.dangerLevel,
                "window1Count": reading.window1,
                "window2Count": reading.window2,
                "window3Count": reading.window3,
            },
        }
    }


def insert(reading: Reading, nodeID: int):
    sensorId = config.nodeID_to_sensorId(nodeID)
    sensorPath = config.nodeID_to_sensorPath(nodeID)
    originator = config.originator

    mobius_payload: dict = to_mobius_payload(reading, sensorId)

    requests.post(
        f"{config.host}:{config.port}/{sensorPath}",
        headers={
            "X-M2M-Origin": originator,
            "Content-Type": "application/vnd.onem2m-res+json;ty=4",
            "X-M2M-RI": str(int(datetime.now().timestamp() * 1000)),
        },
        json=mobius_payload,
    )

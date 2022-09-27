import json
from datetime import datetime
from os import environ

import requests

from ..database import Reading

# TODO: move to config file
MOBIUS_URL = environ.get("MOBIUS_URL", "http://mobius")
MOBIUS_PORT = environ.get("MOBIUS_PORT", "5002")


# Conversione reading per mobius
def to_mobius_payload(reading: Reading, sensorId: str) -> dict:
    return {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": sensorId,
                    "readingTimestamp": datetime.fromtimestamp(
                        reading["readingID"]
                    ).isoformat(),
                    # "latitude": <latitudine del sensore>, // opzionale
                    # "longitude": <longitudine del sensore>, // opzionale
                    # "heading": <orientazione del sensore>, // opzionale
                }
            },
            "sensorData": {
                "canID": reading["canID"],
                "sensorNumber": reading["sensorNumber"],
                "dangerLevel": reading["dangerLevel"],
                "window1Count": reading["window1_count"],
                "window2Count": reading["window2_count"],
                "window3Count": reading["window3_count"],
            },
        }
    }


def insert(reading: Reading):
    with open("./config/mobius_conversion.json") as f:
        mobius_conversion_table = json.load(f)

    sensorPath = mobius_conversion_table[str(reading["nodeID"])]["sensorPath"]
    sensorId = mobius_conversion_table[str(reading["nodeID"])]["sensorId"]

    mobius_payload: dict = to_mobius_payload(reading, sensorId)

    requests.post(
        f"{MOBIUS_URL}:{MOBIUS_PORT}/{sensorPath}",
        json=mobius_payload,
    )

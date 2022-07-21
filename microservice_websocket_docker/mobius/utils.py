import requests
import json
from os import environ
from flask_api import status


MOBIUS_URL = environ.get("MOBIUS_URL", "http://localhost")
MOBIUS_PORT = environ.get("MOBIUS_PORT", "5002")

# Conversione payload chirpstack in payload per mobius
def to_mobius_payload(record: dict) -> dict:
    sensorId = record["data"]["mobius_sensorId"]
    readingTimestamp = record['publishedAt']

    return {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": sensorId,
                    "readingTimestamp": readingTimestamp,
                },
            },
            "sensorData": record,
        }
    }

def insert(record):
    mobius_payload: dict = to_mobius_payload(record)

    requests.post(f"{MOBIUS_URL}:{MOBIUS_PORT}/{record['data']['mobius_sensorPath']}", json=mobius_payload)


def read(sensor_path):
    # Querying mobius for sensor_path
    response: requests.Response = requests.get(f"{MOBIUS_URL}:{MOBIUS_PORT}/{sensor_path}")
    decoded_response: dict = json.loads(response.content)

    collect: list[dict] = decoded_response["m2m:rsp"]["m2m:cin"] \
                            if status.is_success(response.status_code) \
                            else []

    return collect

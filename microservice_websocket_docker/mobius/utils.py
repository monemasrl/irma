import requests
import json
from os import environ
from flask_api import status
from flask import jsonify


MOBIUS_URL = environ.get("MOBIUS_URL", "http://localhost")
MOBIUS_PORT = environ.get("MOBIUS_PORT", "5002")

# Conversione payload chirpstack in payload per mobius
def to_mobius_payload(record: dict) -> dict:
    sensorId = record["tags"]["sensorId"]
    readingTimestamp = record['publishedAt']
    latitude = record['rxInfo'][0]['location']['latitude']
    longitude = record['rxInfo'][0]['location']['longitude']

    return {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": sensorId,
                    "readingTimestamp": readingTimestamp,
                    "latitude": latitude,
                    "longitude": longitude,
                },
            },
            "sensorData": record,
        }
    }

def insert(record):
    mobius_payload: dict = to_mobius_payload(record)

    requests.post(f"{MOBIUS_URL}:{MOBIUS_PORT}/{record['tags']['sensor_path']}", json=mobius_payload)

    return jsonify(mobius_payload)

def read(sensor_path):
    # Querying mobius for sensor_path
    response: requests.Response = requests.get(f"{MOBIUS_URL}:{MOBIUS_PORT}/{sensor_path}")
    decoded_response: dict = json.loads(response.content)

    collect: list[dict] = decoded_response["m2m:rsp"]["m2m:cin"] \
                            if status.is_success(response.status_code) \
                            else []

    return collect
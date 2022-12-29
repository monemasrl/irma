from datetime import datetime

import requests

from config import get_config


# Conversione reading per mobius
def mobius_payload(sensorId: str, now: datetime, sensor_data: dict) -> dict:
    return {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": sensorId,
                    "readingTimestamp": now.isoformat(),
                    # "latitude": <latitudine del sensore>, // opzionale
                    # "longitude": <longitudine del sensore>, // opzionale
                    # "heading": <orientazione del sensore>, // opzionale
                }
            },
            "sensorData": sensor_data,
        }
    }


def send(nodeID: int, data: dict):
    config = get_config()

    mobius_node_info = config.mobius.conversion.get(nodeID)
    if not mobius_node_info:
        print(f"[ERROR] Conversion entry for nodeID '{nodeID}' not found")
        return

    sensorId, sensorPath = mobius_node_info.sensorId, mobius_node_info.sensorPath

    originator = config.mobius.originator

    now = datetime.now()

    requests.post(
        f"{config.mobius.host}:{config.mobius.port}/{sensorPath}",
        headers={
            "X-M2M-Origin": originator,
            "Content-Type": "application/vnd.onem2m-res+json;ty=4",
            "X-M2M-RI": str(int(now.timestamp() * 1000)),
        },
        json=mobius_payload(sensorId, now, data),
    )

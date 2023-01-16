from datetime import datetime

import requests
from pydantic import BaseModel


class Data(BaseModel):
    payloadType: str

    nodeID: int
    canID: int
    sensorNumber: int

    sessionID: int
    readingID: int

    value: int


def insert(data: Data):
    requests.post(
        f"onem2m.labtlclivorno.it/Mobius/RILEVATORI_IRMA/{data.sessionID}",
        headers={
            "X-M2M-Origin": "MONEMA",
            "Content-Type": "application/json;ty=4",
            "X-M2M-RI": str(int(datetime.now().timestamp() * 1000)),
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
                    "rn": "247000034-3",
                }
            }
        },
    )


def create_session(sessionID: int):
    requests.post(
        "onem2m.labtlclivorno.it/Mobius/RILEVATORI_IRMA",
        headers={
            "Content-Type": "application/json;ty=3",
            "X-M2M-RI": str(int(datetime.now().timestamp() * 1000)),
            "X-M2M-Origin": "MONEMA",
        },
        json={"m2m:cnt": {"rn": str(sessionID)}},
    )

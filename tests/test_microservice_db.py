from mockHttp import microservice_db
from fixtures.db_fixtures import *


def test_Payload_to_json(payload: microservice_db.Payload):
    payload_dict = {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": payload.sensorId,
                    "readingTimestamp": payload.readingTimestamp,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                }
            },
            "sensorData": payload.sensorData,
        }
    }

    assert payload.to_json() == payload_dict, \
    "Error in `Payload.to_json`: output mismatch"


def test_SentDocument_to_jsonSent():
    sentDocument = microservice_db.SentDocument(
        eui=123,
        status="rec",
        code=456,
        titolo1="Titolo 1",
        dato1=7.89,
        titolo2="",
        dato2=-2,
        titolo3="Titolo 3!",
        dato3=-3j
    )

    sentDocument_dict = {
        "devEUI": 123,
        "state": "rec",
        "code": 456,
        "datiInterni": [
            {
                "titolo": "Titolo 1",
                "dato": 7.89
            },
            {
                "titolo": "",
                "dato": -2
            },
            {
                "titolo": "Titolo 3!",
                "dato": -3j
            }
        ]
    }

    assert sentDocument.to_json() == sentDocument_dict, \
    "Error in `SentDocument.to_jsonSent()`: output mismatch"

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


def test_SentDocument_to_json(sentDocument: microservice_db.SentDocument):
    sentDocument_dict = {
        "devEUI": sentDocument.eui,
        "state": sentDocument.state,
        "code": sentDocument.code,
        "datiInterni": [
            {
                "titolo": sentDocument.titolo1,
                "dato": sentDocument.dato1
            },
            {
                "titolo": sentDocument.titolo2,
                "dato": sentDocument.dato2
            },
            {
                "titolo": sentDocument.titolo3,
                "dato": sentDocument.dato3
            }
        ]
    }

    assert sentDocument.to_json() == sentDocument_dict, \
    "Error in `SentDocument.to_jsonSent()`: output mismatch"

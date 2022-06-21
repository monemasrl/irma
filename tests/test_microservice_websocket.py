from mockHttp import microservice_websocket

def test_Payload_to_json():
    payload = microservice_websocket.Payload(
        iD="abc",
        time=123,
        latitude=45.7,
        longitude=23.5,
        sensorData=3
    )

    payload_dict = {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": "abc",
                    "readingTimestamp": 123,
                    "latitude": 45.7,
                    "longitude": 23.5,
                }
            },
            "sensorData": 3,
        }
    }

    assert payload.to_json() == payload_dict, "Error in `Payload.to_json`: output mismatch"


def test_SentDocument_to_jsonSent():
    sentDocument = microservice_websocket.SentDocument(
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

    assert sentDocument.to_jsonSent() == sentDocument_dict, "Error in `SentDocument.to_jsonSent()`: output mismatch"


def test_prepareData():
    data = """{"sensorData": 123}"""

    assert microservice_websocket.prepareData(data) == 123, "Error in `prepareData()`: output mismatch"
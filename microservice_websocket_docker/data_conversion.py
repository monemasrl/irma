import base64


def decode_devEUI(encoded_devEUI: str) -> str:
    return base64.b64decode(encoded_devEUI).hex()


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
        

# Creazione payload per irma-ui
def to_irma_ui_data(
        devEUI: str,
        applicationID: str,
        sensorId: str,
        state: str,
        titolo1: str,
        titolo2: str,
        titolo3: str,
        dato1: float,
        dato2: float,
        dato3: int,
    ) -> dict:

    return {
        "devEUI": devEUI,
        "applicationID": applicationID,
        "sensorId": sensorId,
        "state": state,
        "datiInterni": [
            {
                "titolo": titolo1,
                "dato": dato1
            },
            {
                "titolo": titolo2,
                "dato": dato2
            },
            {
                "titolo": titolo3,
                "dato": dato3
            },
        ],
    }

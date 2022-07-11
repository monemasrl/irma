
# Conversione payload chirpstack in payload per mobius
def to_mobius_payload(record: dict) -> dict:
    sensorId = record['applicationID']
    readingTimestamp = record['publishedAt']
    latitude = record['rxInfo'][0]['location']['latitude']
    longitude = record['rxInfo'][0]['location']['longitude']
    sensorData = record

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
            "sensorData": sensorData,
        }
    }
        

# Creazione payload per irma-ui
def to_irma_ui_data(
        eui: str,
        state: str,
        code: str,
        titolo1: str,
        titolo2: str,
        titolo3: str,
        dato1: float,
        dato2: float,
        dato3: int,
    ) -> dict:

    return {
        "devEUI":eui,
        "state": state,
        "code": code,
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

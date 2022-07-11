from microservice_websocket import data_conversion
from fixtures.data_fixtures import *


def test_to_mobius_payload(sensorData_Uplink: dict):
    """
    Coherence test for to_mobius_payload() function
    """

    expected_value = {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": sensorData_Uplink['applicationID'],
                    "readingTimestamp": sensorData_Uplink['publishedAt'],
                    "latitude": sensorData_Uplink['rxInfo'][0]['location']['latitude'],
                    "longitude": sensorData_Uplink['rxInfo'][0]['location']['longitude'],
                }
            },
            "sensorData": sensorData_Uplink,
        }
    }

    assert data_conversion.to_mobius_payload(sensorData_Uplink) == expected_value, \
    "Error in `to_mobius_payload`: output mismatch"


def test_to_irma_ui():
    eui = "123"
    state = "ok"
    code = "2034823940"
    titolo1 = "Foo"
    titolo2 = "Bar"
    titolo3 = "Baz"
    dato1 = 0.0
    dato2 = 0.0
    dato3 = 0

    expected_value = {
        "devEUI": eui,
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
            }
        ]
    }

    assert data_conversion.to_irma_ui_data(
        eui, state, code,
        titolo1, titolo2, titolo3,
        dato1, dato2, dato3
    ) == expected_value, "Error in `to_irma_ui_data`: output mismatch"


def test_decode_devEUI(devEUI):
    assert data_conversion.decode_devEUI(devEUI) == "0202020202020202", \
    "Error in `decode_devEUI()`: output mismatch"


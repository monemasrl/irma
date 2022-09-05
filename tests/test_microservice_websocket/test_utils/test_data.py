from microservice_websocket.app.utils.data import (
    decode_data,
    encode_mqtt_data,
    to_dashboard_data,
)


def test_decode_data():
    encoded_data: str = "AQAAAAdtb2JpdXNJZCAgbW9iaXVzUGF0aA=="

    expected_output = {
        "payloadType": 1,
        "sensorData": 7,
        "mobius_sensorId": "mobiusId",
        "mobius_sensorPath": "mobiusPath",
    }

    assert (
        decode_data(encoded_data) == expected_output
    ), "Error in `decode_data`: output mismatch"


def test_encode_mqtt_data():
    command: int = 1
    iso_timestamp: str = "2022-08-23T11:06:00.676497"

    expected_output: bytes = b"ATIwMjItMDgtMjNUMTE6MDY6MDAuNjc2NDk3"

    assert (
        encode_mqtt_data(command, iso_timestamp) == expected_output
    ), "Error in `encode_mqtt_data`: output mismatch"


def test_to_dashboard_data():
    sensorID = "2288300834"
    sensorName = "123"
    applicationID = "123234"
    state = "ok"
    titolo1 = "Foo"
    titolo2 = "Bar"
    titolo3 = "Baz"
    dato1 = 0.0
    dato2 = 0.0
    dato3 = 0
    unhandledAlertIDs = [1, 2, 3, 4]

    expected_value = {
        "sensorID": sensorID,
        "sensorName": sensorName,
        "applicationID": applicationID,
        "state": state,
        "datiInterni": [
            {"titolo": titolo1, "dato": dato1},
            {"titolo": titolo2, "dato": dato2},
            {"titolo": titolo3, "dato": dato3},
        ],
        "unhandledAlertIDs": unhandledAlertIDs,
    }

    assert (
        to_dashboard_data(
            sensorID,
            sensorName,
            applicationID,
            state,
            titolo1,
            titolo2,
            titolo3,
            dato1,
            dato2,
            dato3,
            unhandledAlertIDs,
        )
        == expected_value
    ), "Error in `to_irma_ui_data`: output mismatch"

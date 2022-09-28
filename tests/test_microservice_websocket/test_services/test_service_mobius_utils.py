from datetime import datetime

from microservice_websocket.app.services.mobius.utils import to_mobius_payload


def test_to_mobius_payload(reading):
    """
    Coherence test for to_mobius_payload() function
    """
    sensorId: str = "foo_bar_Id"

    expected_value = {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": sensorId,
                    "readingTimestamp": datetime.fromtimestamp(
                        reading["readingID"]
                    ).isoformat(),
                }
            },
            "sensorData": {
                "canID": reading["canID"],
                "sensorNumber": reading["sensorNumber"],
                "dangerLevel": reading["dangerLevel"],
                "window1Count": reading["window1_count"],
                "window2Count": reading["window2_count"],
                "window3Count": reading["window3_count"],
            },
        }
    }

    assert (
        to_mobius_payload(reading, sensorId) == expected_value
    ), "Error in `to_mobius_payload`: output mismatch"

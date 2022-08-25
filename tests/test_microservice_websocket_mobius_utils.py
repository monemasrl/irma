from microservice_websocket_docker.mobius.utils import to_mobius_payload


def test_to_mobius_payload(node_data: dict):
    """
    Coherence test for to_mobius_payload() function
    """

    expected_value = {
        "m2m:cin": {
            "con": {
                "metadata": {
                    "sensorId": node_data["data"]["mobius_sensorId"],
                    "readingTimestamp": node_data["publishedAt"],
                }
            },
            "sensorData": node_data,
        }
    }

    assert (
        to_mobius_payload(node_data) == expected_value
    ), "Error in `to_mobius_payload`: output mismatch"

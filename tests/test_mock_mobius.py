import json
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from mobius_adapter.utils import mobius_payload
from mock_mobius import app as mobius_app


class TestFlaskApp:
    @pytest.fixture()
    def app(self) -> Flask:  # type: ignore
        app = mobius_app.create_app("config_testing.json")
        # set up
        yield app
        # clean up

    @pytest.fixture()
    def app_client(self, app: Flask) -> FlaskClient:
        return app.test_client()

    def test_publish_data(self, app_client, sensor_data: dict):
        sensorId = "sensorId1_foo"
        sensorPath = "sensorPath1_foo"

        payload: dict = mobius_payload(sensorId, datetime.now(), sensor_data)
        print(payload)
        response: TestResponse = app_client.post(f"/{sensorPath}", json=payload)

        assert (
            response.status_code == 200
        ), "Invalid response code from server when submitting valid payload"

        response = app_client.post("/", json=payload)

        assert (
            response.status_code == 404
        ), "Invalid response code from server when submitting on invalid route"

    def test_db_consistency(self, app_client, sensor_data: dict):
        """
        This test is meant to check if data stored
        as Reading in database is consistent
        """

        sensorId = "sensorId1_foo"
        sensorPath = "sensorPath1_foo"
        payload: dict = mobius_payload(sensorId, datetime.now(), sensor_data)

        response: TestResponse = app_client.post(f"/{sensorPath}", json=payload)

        assert (
            response.status_code == 200
        ), "Invalid response code from server when submitting valid payload"

        data = app_client.get(f"/{sensorPath}").data
        data_dict: dict = json.loads(data.decode())

        print(data_dict)
        assert (
            "m2m:rsp" in data_dict and "m2m:cin" in data_dict["m2m:rsp"]
        ), "Invalid structure of response from server when querying /<SENSOR_PATH>"

        assert (
            len(data_dict["m2m:rsp"]["m2m:cin"]) > 0
        ), "Reading doesn't get saved on the database"

    def test_db_query_limits(self, app_client, sensor_data: dict):
        sensorId = "sensorId1_foo"
        sensorPath = "sensorPath1_foo"

        reading_timestamps = [
            datetime(2022, 7, 10, 12, 45, x) for x in [10, 20, 30, 40, 50]
        ]

        for time in reading_timestamps:
            payload: dict = mobius_payload(sensorId, time, sensor_data)

            response: TestResponse = app_client.post(f"/{sensorPath}", json=payload)

            assert (
                response.status_code == 200
            ), "Invalid response code from server when submitting valid payload"

        inf_limit: str = reading_timestamps[0].strftime("%Y%m%dT%H%M%S")
        sup_limit: str = reading_timestamps[-1].strftime("%Y%m%dT%H%M%S")
        response = app_client.get(f"/{sensorPath}?crb={sup_limit}&cra={inf_limit}")

        assert (
            response.status_code == 200
        ), "Invalid response code from server when querying with time limits"

        decoded_response: dict = json.loads(response.data)
        assert (
            "m2m:rsp" in decoded_response and "m2m:cin" in decoded_response["m2m:rsp"]
        ), "Invalid structure of response from server when querying /<SENSOR_PATH>"

        assert (
            len(decoded_response["m2m:rsp"]["m2m:cin"]) == 3
        ), f"Invalid response from server, expected 3 results \
            but got {len(decoded_response['m2m:rsp']['m2m:cin'])}"

        response = app_client.get(
            f"/{sensorPath}?crb={sup_limit}&cra={inf_limit}&lim=2"
        )

        assert (
            response.status_code == 200
        ), "Invalid response code from server when querying \
            with time limits and quantity limits"

        decoded_response: dict = json.loads(response.data)
        assert (
            "m2m:rsp" in decoded_response and "m2m:cin" in decoded_response["m2m:rsp"]
        ), "Invalid structure of response from server when querying /<SENSOR_PATH>"

        assert (
            len(decoded_response["m2m:rsp"]["m2m:cin"]) == 2
        ), f"Invalid response from server, expected 2 results \
            but got {len(decoded_response['m2m:rsp']['m2m:cin'])}"

    def test_db_query_last(self, app_client):
        sensorPath = "sensorPath1_foo"

        response: TestResponse = app_client.get(f"/{sensorPath}")
        decoded_response: dict = json.loads(response.data)

        readings = [x for x in decoded_response["m2m:rsp"]["m2m:cin"]]

        readings.sort(
            key=lambda x: x["con"]["metadata"]["readingTimestamp"], reverse=True
        )
        last_reading: dict = readings[0]

        response = app_client.get(f"/{sensorPath}/la")

        assert (
            response.status_code == 200
        ), "Invalid response code from server when querying last sensor reading"

        decoded_response = json.loads(response.data)

        assert (
            "m2m:cin" in decoded_response
        ), "Invalid response structure when querying last sensor reading: \
        expected 'm2m:cin' in response json"

        assert (
            decoded_response["m2m:cin"] == last_reading
        ), "Invalid response when querying last sensor reading: it is not the latest"

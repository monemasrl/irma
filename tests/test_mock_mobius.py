from flask import Flask
from flask.testing import FlaskClient
from flask_api import status
from werkzeug.test import TestResponse
from datetime import datetime
import mock_mobius
import pytest
import json
from microservice_websocket.data_conversion import to_mobius_payload
from fixtures.data_fixtures import *


class TestFlaskApp:

    @pytest.fixture()
    def app(self) -> Flask: # type: ignore
        app = mock_mobius.create_app("config_testing.json")
        # set up
        yield app
        # clean up

    @pytest.fixture()
    def app_client(self, app: Flask) -> FlaskClient:
        return app.test_client()

    def test_publish_data(self, app_client, sensorData_Uplink):
        payload: dict = to_mobius_payload(sensorData_Uplink)
        print(payload)
        response: TestResponse = app_client.post(
            f"/{sensorData_Uplink['applicationID']}", json=payload)

        assert status.is_success(response.status_code), \
        "Invalid response code from server when submitting valid payload"

        response = app_client.post("/", json=payload)

        assert status.is_client_error(response.status_code), \
        "Invalid response code from server when submitting on invalid route"

    def test_db_consistency(self, app_client, sensorData_Uplink: dict):
        """
        This test is meant to check if data stored
        as Reading in database is consistent
        """
        payload: dict = to_mobius_payload(sensorData_Uplink)
        response: TestResponse = app_client.post(
            f"/{sensorData_Uplink['applicationID']}", json=payload)

        assert status.is_success(response.status_code), \
        "Invalid response code from server when submitting valid payload"

        data = app_client.get(f"/{sensorData_Uplink['applicationID']}").data
        data_dict: dict = json.loads(data.decode())

        print(data_dict)
        assert "m2m:rsp" in data_dict and "m2m:cin" in data_dict['m2m:rsp'], \
        "Invalid structure of response from server when querying /<SENSOR_PATH>"

        assert len(data_dict["m2m:rsp"]["m2m:cin"]) > 0, \
        "Reading doesn't get saved on the database"

    def test_db_query_limits(self, app_client, sensorData_Uplink: dict):
        reading_timestamps = [datetime(2022, 7, 10, 12, 45, x) for x in [10, 20, 30, 40, 50]]
        reading_timestamps_iso = [x.isoformat() for x in reading_timestamps]

        for time in reading_timestamps_iso:
            sensorData_Uplink['publishedAt'] = time
            payload: dict = to_mobius_payload(sensorData_Uplink)

            response: TestResponse = app_client.post(
                f"/{sensorData_Uplink['applicationID']}", json=payload)

            assert status.is_success(response.status_code), \
            "Invalid response code from server when submitting valid payload"

        inf_limit: str = reading_timestamps[0].strftime("%Y%m%dT%H%M%S")
        sup_limit: str = reading_timestamps[-1].strftime("%Y%m%dT%H%M%S")
        response = app_client.get(
            f"/{sensorData_Uplink['applicationID']}?crb={sup_limit}&cra={inf_limit}"
        ) 

        assert status.is_success(response.status_code), \
        "Invalid response code from server when querying with time limits"

        decoded_response: dict = json.loads(response.data) 
        assert "m2m:rsp" in decoded_response and "m2m:cin" in decoded_response['m2m:rsp'], \
        "Invalid structure of response from server when querying /<SENSOR_PATH>"

        assert len(decoded_response["m2m:rsp"]["m2m:cin"]) == 3, \
        f"Invalid response from server, expected 3 results but got {len(decoded_response['m2m:rsp']['m2m:cin'])}"

        response = app_client.get(
            f"/{sensorData_Uplink['applicationID']}?crb={sup_limit}&cra={inf_limit}&lim=2"
        ) 

        assert status.is_success(response.status_code), \
        "Invalid response code from server when querying with time limits and quantity limits"

        decoded_response: dict = json.loads(response.data) 
        assert "m2m:rsp" in decoded_response and "m2m:cin" in decoded_response['m2m:rsp'], \
        "Invalid structure of response from server when querying /<SENSOR_PATH>"

        assert len(decoded_response["m2m:rsp"]["m2m:cin"]) == 2, \
        f"Invalid response from server, expected 2 results but got {len(decoded_response['m2m:rsp']['m2m:cin'])}"

    def test_db_query_last(self, app_client, sensorData_Uplink: dict):
        response: TestResponse = app_client.get(f"/{sensorData_Uplink['applicationID']}")
        decoded_response: dict = json.loads(response.data)

        readings = [x for x in decoded_response["m2m:rsp"]["m2m:cin"]]

        readings.sort(key=lambda x: x["con"]["metadata"]["readingTimestamp"], reverse=True)
        last_reading: dict = readings[0]

        response = app_client.get(f"/{sensorData_Uplink['applicationID']}/la")

        assert status.is_success(response.status_code), \
        "Invalid response code from server when querying last sensor reading"

        decoded_response = json.loads(response.data)

        assert "m2m:cin" in decoded_response, \
        "Invalid response structure when querying last sensor reading: \
        expected 'm2m:cin' in response json"

        assert decoded_response["m2m:cin"] == last_reading, \
        "Invalid response when querying last sensor reading: it is not the latest"

from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient
from mock import patch

from microservice_websocket.app import create_app, socketio
from microservice_websocket.app.services.database import Reading
from tests.test_microservice_websocket.blueprint_test_routes import test_bp


@pytest.fixture()
def isoTimestamp() -> str:
    """
    Time format received from chirpstack.
    It does follow the ISO8601 standard.
    """
    return "2013-03-31T16:21:17.528002Z"


@pytest.fixture()
def node_data() -> dict:
    return {
        "sensorID": 1,
        "sensorName": "irma-sensor",
        "applicationID": "foo",
        "organizationID": "bar",
        "data": {
            "state": 3,
            "sensorData": 4.5,
            "mobius_sensorId": "foo",
            "mobius_sensorPath": "bar",
        },
        "publishedAt": "time",
        "payloadType": 1,
    }


@pytest.fixture()
def testing_app() -> Flask:
    with patch("microservice_websocket.app.DISABLE_MQTT", True):
        app = create_app(testing=True)

    app.register_blueprint(test_bp)

    # set up
    yield app
    # clean up


@pytest.fixture()
def testing_socketio() -> SocketIO:
    return socketio


@pytest.fixture()
def app_client(testing_app: Flask) -> FlaskClient:
    return testing_app.test_client()


@pytest.fixture()
def socketio_client(
    testing_app: Flask, app_client: FlaskClient, testing_socketio: SocketIO
) -> SocketIOTestClient:
    return socketio.test_client(testing_app, flask_test_client=app_client)


@pytest.fixture()
def tokens(app_client: FlaskClient) -> tuple[str, str]:
    response = app_client.post(
        "/api/jwt/authenticate",
        json={"username": "bettarini@monema.it", "password": "password"},
    )

    decoded_json = response.json

    return [decoded_json["access_token"], decoded_json["refresh_token"]]


@pytest.fixture()
def auth_header(tokens):
    return {"Authorization": f"Bearer {tokens[0]}"}


@pytest.fixture()
def refresh_header(tokens):
    return {"Authorization": f"Bearer {tokens[1]}"}


@pytest.fixture()
def obj_id() -> str:
    return "63186eab0ca2d54a5c258384"


@pytest.fixture()
def reading() -> Reading:
    return Reading(
        nodeID=1,
        canID=2,
        sensorNumber=1,
        readingID=1_640_200,
        sessionID=1_640_000,
        dangerLevel=4,
        window1_count=111,
        window2_count=222,
        window3_count=333,
        publishedAt=datetime.now(),
    )

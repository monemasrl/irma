from datetime import datetime

import pytest
from beanie import PydanticObjectId
from fastapi.testclient import TestClient
from test_microservice_websocket.router_test_routes import test_router

from microservice_websocket.app import app
from microservice_websocket.app.services.database import Reading

# @pytest.fixture()
# def isoTimestamp() -> str:
#     """
#     Time format received from chirpstack.
#     It does follow the ISO8601 standard.
#     """
#     return "2013-03-31T16:21:17.528002Z"
#
#
# @pytest.fixture()
# def node_data() -> dict:
#     return {
#         "sensorID": 1,
#         "sensorName": "irma-sensor",
#         "applicationID": "foo",
#         "organizationID": "bar",
#         "data": {
#             "state": 3,
#             "sensorData": 4.5,
#             "mobius_sensorId": "foo",
#             "mobius_sensorPath": "bar",
#         },
#         "publishedAt": "time",
#         "payloadType": 1,
#     }


# @pytest.fixture()
# def testing_socketio() -> Client:
#     return socketio


@pytest.fixture
def app_client() -> TestClient:
    app.include_router(test_router)
    with TestClient(app) as client:
        return client


# @pytest.fixture()
# def socketio_client(
#     testing_app: Flask, app_client: FlaskClient, testing_socketio: SocketIO
# ) -> SocketIOTestClient:
#     return socketio.test_client(testing_app, flask_test_client=app_client)


@pytest.fixture
def token(app_client: TestClient) -> str:
    response = app_client.post(
        "/api/jwt/authenticate",
        json={"email": "foo@bar.com", "password": "baz"},
    )

    decoded_json = response.json()

    return decoded_json["access_token"]


@pytest.fixture()
def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


# @pytest.fixture()
# def refresh_header(tokens):
#     return {"Authorization": f"Bearer {tokens[1]}"}


@pytest.fixture()
def obj_id() -> str:
    return "63186eab0ca2d54a5c258384"


@pytest.fixture()
def reading(obj_id: str) -> Reading:
    return Reading(
        node=PydanticObjectId(obj_id),
        canID=2,
        sensorNumber=1,
        readingID=1_640_200,
        sessionID=1_640_000,
        dangerLevel=4,
        window1=111,
        window2=222,
        window3=333,
        publishedAt=datetime.now(),
    )

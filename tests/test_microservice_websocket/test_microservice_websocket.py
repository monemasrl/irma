from unittest.mock import mock_open

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient
from mock import patch

from microservice_websocket.app import create_app, socketio
from microservice_websocket.app.services.database import Application, Organization
from tests.test_microservice_websocket.test_routes import test_bp


class TestFlaskApp:
    # --------------- Fixtures ---------------------------------------------
    @pytest.fixture()
    def testing_app(self) -> Flask:
        with patch("microservice_websocket.app.DISABLE_MQTT", True):
            app = create_app(testing=True)

        app.register_blueprint(test_bp)

        # set up
        yield app
        # clean up

    @pytest.fixture()
    def testing_socketio(self) -> SocketIO:
        return socketio

    @pytest.fixture()
    def app_client(self, testing_app: Flask) -> FlaskClient:
        return testing_app.test_client()

    @pytest.fixture()
    def socketio_client(
        self, testing_app: Flask, app_client: FlaskClient, testing_socketio: SocketIO
    ) -> SocketIOTestClient:
        return socketio.test_client(testing_app, flask_test_client=app_client)

    @pytest.fixture()
    def jwt_token(self, app_client: FlaskClient):
        response = app_client.post(
            "/api/jwt/authenticate",
            json={"username": "bettarini@monema.it", "password": "password"},
        )

        decoded_json = response.json

        return decoded_json["access_token"]

    #
    # ------------------- utils/api_token.py -------------------------------
    def test_api_token_decorator(self, app_client: FlaskClient):
        endpoint = "/test/api-token-test"

        response = app_client.get(endpoint)

        assert (
            response.status_code == 401
        ), "Invalid response code from route protected with @api_token_required"

        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.get(
                endpoint, headers={"Authorization": "Bearer 1234"}
            )

        assert (
            response.status_code == 200
        ), "Cannot access route protected with @api_token_required with correct api-token"

    #
    # ------------------ blueprints/api/organization.py --------------------
    def test_create_organizations(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/organizations/"
        name = "orgName"

        # Creating Organization
        payload = {"name": name}
        response = app_client.post(
            endpoint, json=payload, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when posting valid data"

        assert (
            len(Organization.objects()) == 1
        ), "Create organization doesn't persist in the database"

        # Creating Organization with already used name
        response = app_client.post(
            endpoint, json=payload, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting data with name already in use"

        assert (
            len(Organization.objects()) == 1
        ), "Create organization doesn't persist in the database"

        assert (
            Organization.objects().first()["organizationName"] == name
        ), "Invalid organization name"

        # Creating organization with invalid payload
        response = app_client.post(
            endpoint, json={}, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting an invalid payload when creating an organization"

        Organization.objects().first().delete()

    def test_get_organizations(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/organizations/"
        name = "orgName"

        # Getting empty Organizations
        response = app_client.get(
            endpoint, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when getting route with empty organizations"

        # Manual create Organization
        o = Organization(organizationName=name)
        o.save()

        # Getting newly created Organization
        response = app_client.get(
            endpoint, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting route with organizations present"

        assert (
            len(response.json["organizations"]) == 1
        ), "Invalid payload lenght when querying organizations"

        assert (
            response.json["organizations"][0]["organizationName"] == name
        ), "Invalid Organization name"

        # Teardown
        o.delete()

    #
    # ------------------ blueprints/api/application.py ---------------------
    def test_create_applications(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/applications/"
        name = "appName"
        o = Organization(organizationName="orgName")
        o.save()
        organizationID = str(Organization.objects().first()["id"])

        # Creating Application
        response = app_client.post(
            endpoint + organizationID,
            json={"name": name},
            headers={"Authorization": f"Bearer {jwt_token}"},
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when posting valid data in create route"

        # Creating application with wrong orgID
        response = app_client.post(
            endpoint + "63186eab0ca2d54a5c258384",
            json={"name": "qux"},
            headers={"Authorization": f"Bearer {jwt_token}"},
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when posting data to wrong orgID"

        # Creating application with same name
        response = app_client.post(
            endpoint + organizationID,
            json={"name": name},
            headers={"Authorization": f"Bearer {jwt_token}"},
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting data with already existing name"

        # Creating application with invalid payload
        response = app_client.post(
            endpoint + organizationID,
            json={},
            headers={"Authorization": f"Bearer {jwt_token}"},
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting invalid data"

        # Teardown
        Application.objects().first().delete()
        o.delete()

    def test_get_applications(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/applications/"
        name = "appName"
        o = Organization(organizationName="orgName")
        o.save()
        organizationID = str(Organization.objects().first()["id"])

        # Getting empty Applications with no args
        response = app_client.get(
            endpoint, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when getting Application with no args"

        # Getting empty Applications with right args
        response = app_client.get(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            query_string={"organizationID": organizationID},
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when getting Application with right args"

        # Manually create application
        a = Application(applicationName=name, organization=o)
        a.save()

        # Getting newly created application
        response = app_client.get(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            query_string={"organizationID": organizationID},
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting Application"

        # Teardown
        a.delete()
        o.delete()

    # @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    # def test_socketio_emits_on_change(
    #         self,
    #         app_client: FlaskClient,
    #         socketio_client: SocketIOTestClient,
    #         sensorData_Uplink: dict):
    #     app_client.post("/publish", json=sensorData_Uplink)
    #     received: list = socketio_client.get_received()
    #     assert received[0]['name'] == 'change', \
    #     "Invalid response from socket 'onChange()'"

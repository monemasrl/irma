from datetime import datetime
from unittest.mock import mock_open

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient
from mock import patch

from microservice_websocket.app import create_app, socketio
from microservice_websocket.app.services import database as db
from microservice_websocket.app.utils.enums import PayloadType
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
        db.Organization.drop_collection()
        db.Application.drop_collection()
        db.Role.drop_collection()
        db.User.drop_collection()
        db.Node.drop_collection()
        db.Reading.drop_collection()
        db.Alert.drop_collection()

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
            len(db.Organization.objects()) == 1
        ), "Create organization doesn't persist in the database"

        # Creating Organization with already used name
        response = app_client.post(
            endpoint, json=payload, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting data with name already in use"

        assert (
            len(db.Organization.objects()) == 1
        ), "Create organization doesn't persist in the database"

        assert (
            db.Organization.objects().first()["organizationName"] == name
        ), "Invalid organization name"

        # Creating organization with invalid payload
        response = app_client.post(
            endpoint, json={}, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting an invalid payload when creating an organization"

        db.Organization.objects().first().delete()

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
        o = db.Organization(organizationName=name)
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
        o = db.Organization(organizationName="orgName")
        o.save()
        organizationID = str(db.Organization.objects().first()["id"])

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
        db.Application.objects().first().delete()
        o.delete()

    def test_get_applications(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/applications/"
        name = "appName"
        o = db.Organization(organizationName="orgName")
        o.save()
        organizationID = str(db.Organization.objects().first()["id"])

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
        a = db.Application(applicationName=name, organization=o)
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

    #
    # ------------------ blueprints/api/node.py ----------------------------
    def test_get_nodes(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/nodes/"
        o = db.Organization(organizationName="foo")
        o.save()
        a = db.Application(applicationName="bar", organization=o)
        a.save()
        applicationID = str(a["id"])

        # Getting nodes with no args
        response = app_client.get(
            endpoint, headers={"Authorization": f"Bearer {jwt_token}"}
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when getting node with no args"

        # Getting nodes with no node present
        response = app_client.get(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            query_string={"applicationID": applicationID},
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when getting empty nodes"

        # Manually create node
        n = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a,
            organization=o,
            state=1,
            lastSeenAt=datetime.now(),
        )
        n.save()

        # Getting newly created node
        response = app_client.get(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            query_string={"applicationID": applicationID},
        )

        assert response.status_code == 200, "Invalid response code when getting nodes"

        # Teardown
        n.delete()
        a.delete()
        o.delete()

    #
    # ------------------ blueprints/api/alert.py ---------------------------
    def test_handle_alert(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/alert/handle"
        org = db.Organization(organizationName="foo")
        org.save()
        app = db.Application(applicationName="bar", organization=org)
        app.save()
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=app,
            organization=org,
            state=1,
            lastSeenAt=datetime.now(),
        )
        node.save()
        reading = db.Reading(
            nodeID=node["nodeID"],
            canID=1,
            sensorNumber=2,
            readingID=32704,
            sessionID=12892,
            publishedAt=datetime.now(),
        )
        reading.save()

        # Handle not existing alert
        response = app_client.post(
            endpoint,
            json={
                "alertID": "63186eab0ca2d54a5c258384",
                "isConfirmed": True,
                "handleNote": "foo",
            },
            headers={"Authorization": f"Bearer {jwt_token}"},
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to handle non-existing alert"

        # Manually create Alert
        alert = db.Alert(
            reading=reading,
            node=node,
            sessionID=reading["sessionID"],
            isHandled=False,
        )
        alert.save()

        # Try to handle newly created alert
        response = app_client.post(
            endpoint,
            json={
                "alertID": str(alert["id"]),
                "isConfirmed": True,
                "handleNote": "foo",
            },
            headers={"Authorization": f"Bearer {jwt_token}"},
        )

        alert = db.Alert.objects().first()

        assert (
            response.status_code == 200
            and alert["isConfirmed"]
            and alert["handleNote"] == "foo"
            and alert["handledBy"]["email"] == "bettarini@monema.it"
        ), "Invalid response code when trying to handle existing alert"

        # Teardown
        alert.delete()
        reading.delete()
        node.delete()
        app.delete()
        org.delete()

    #
    # ------------------ blueprints/api/jwt.py -----------------------------
    def test_jwt_authenticate(self, app_client: FlaskClient):
        endpoint = "/api/jwt/authenticate"

        # Trying to authenticate with invalid payload
        response = app_client.post(endpoint, json={})

        assert (
            response.status_code == 400
        ), "Invalid response code when trying to authenticate with invalid payload"

        # Trying to authenticate as a non-registered user
        response = app_client.post(
            endpoint, json={"username": "foo", "password": "bar"}
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to authenticate as a non-registered user"

        # Trying to authenticate with wrong password
        response = app_client.post(
            endpoint, json={"username": "bettarini@monema.it", "password": "foo"}
        )

        assert (
            response.status_code == 401
        ), "Invalid response code when trying to authenticate with wrong password"

        # Normal authentication
        response = app_client.post(
            endpoint, json={"username": "bettarini@monema.it", "password": "password"}
        )

        assert (
            response.status_code == 200
            and "access_token" in response.json
            and "refresh_token" in response.json
        ), "Invalid response when posting valid data"

    #
    # ------------------ blueprints/api/payload.py -------------------------
    def test_publish(self, app_client: FlaskClient, jwt_token: str):
        endpoint = "/api/payload/publish"
        org = db.Organization(organizationName="foo")
        org.save()
        app = db.Application(applicationName="bar", organization=org)
        app.save()

        # Trying to post data to non-existing application
        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": "63186eab0ca2d54a5c258384",
                    "organizationID": str(org["id"]),
                    "payloadType": PayloadType.KEEP_ALIVE,
                    "data": {},
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 404
        ), "Invalid response code when posting data to non-existing application"

        # Post data to non-existing node
        total_reading_data = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 3,
            "count": 111,
            "sessionID": 3,
            "readingID": 1,
        }

        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(app["id"]),
                    "organizationID": str(org["id"]),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": total_reading_data,
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert len(db.Node.objects()) == 1, "Couldn't create node upon posting data"
        assert (
            len(db.Reading.objects()) == 1
        ), "Couldn't create reading upon posting data"

        # Teardown
        db.Node.objects().first().delete()
        app.delete()
        org.delete()

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

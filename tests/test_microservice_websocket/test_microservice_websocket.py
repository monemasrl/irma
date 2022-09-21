from datetime import datetime
from unittest.mock import mock_open

from flask.testing import FlaskClient
from mock import patch

from microservice_websocket.app.services import database as db
from microservice_websocket.app.utils.enums import PayloadType


class TestPostApplications:
    endpoint = "/api/applications/"
    name = "appName"

    @classmethod
    def setup_class(cls):
        o = db.Organization(organizationName="orgName")
        o.save()

    @classmethod
    def teardown_class(cls):
        db.Application.drop_collection()
        db.Organization.drop_collection()

    # Creating Application
    def test_create(self, app_client: FlaskClient, auth_header):
        organizationID = str(db.Organization.objects().first()["id"])

        response = app_client.post(
            self.endpoint + organizationID,
            json={"name": self.name},
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when posting valid data in create route"

        assert (
            db.Application.objects().first()["applicationName"] == self.name
        ), "Invalid name for Application object"

    # Creating application with wrong orgID
    def test_create_with_no_org(self, app_client: FlaskClient, auth_header, obj_id):
        response = app_client.post(
            self.endpoint + obj_id, json={"name": "qux"}, headers=auth_header
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when posting data to wrong orgID"

    # Creating application with same name
    def test_create_invalid_name(self, app_client: FlaskClient, auth_header):
        organizationID = str(db.Organization.objects().first()["id"])

        response = app_client.post(
            self.endpoint + organizationID,
            json={"name": self.name},
            headers=auth_header,
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting data with already existing name"

    # Creating application with invalid payload
    def test_create_invalid_payload(self, app_client: FlaskClient, auth_header, obj_id):
        organizationID = str(db.Organization.objects().first()["id"])

        response = app_client.post(
            self.endpoint + organizationID, json={}, headers=auth_header
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting invalid data"

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
        db.Reading.drop_collection()
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

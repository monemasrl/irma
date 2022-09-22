from flask.testing import FlaskClient

from microservice_websocket.app.services import database as db


class TestGetApplications:
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

    # Getting empty Applications with no args
    def test_get_no_args(self, app_client: FlaskClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 400
        ), "Invalid response code when getting Application with no args"

    # Getting empty Applications with right args
    def test_get_no_applications(self, app_client: FlaskClient, auth_header):
        organizationID = str(db.Organization.objects().first()["id"])

        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={"organizationID": organizationID},
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when getting Application with right args"

    # Getting created application
    def test_get(self, app_client: FlaskClient, auth_header):
        # Manually create application
        o = db.Organization.objects().first()
        a = db.Application(applicationName=self.name, organization=o)
        a.save()

        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={"organizationID": str(o["id"])},
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting Application"

        assert (
            response.json["applications"][0]["applicationName"] == self.name
        ), "Invalid Application name"


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

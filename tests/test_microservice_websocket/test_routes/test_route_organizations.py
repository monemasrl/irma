from flask.testing import FlaskClient

from microservice_websocket.app.services import database as db


class TestPostOrganizations:
    endpoint = "/api/organizations/"
    name = "orgName"

    @classmethod
    def teardown_class(cls):
        db.Organization.drop_collection()

    # Creating Organization
    def test_create(self, app_client: FlaskClient, auth_header):
        response = app_client.post(
            self.endpoint,
            json={"name": self.name},
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when posting valid data"

        assert (
            len(db.Organization.objects()) == 1
        ), "Create organization doesn't persist in the database"

        assert (
            db.Organization.objects().first()["organizationName"] == self.name
        ), "Invalid organization name"

    # Creating Organization with already used name
    def test_create_invalid_name(self, app_client: FlaskClient, auth_header):

        response = app_client.post(
            self.endpoint, json={"name": self.name}, headers=auth_header
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting data with name already in use"

    # Creating organization with invalid payload
    def test_create_invalid_payload(self, app_client: FlaskClient, auth_header):
        response = app_client.post(self.endpoint, json={}, headers=auth_header)

        assert (
            response.status_code == 400
        ), "Invalid response code when posting an invalid payload when creating an organization"


class TestGetOrganizations:
    endpoint = "/api/organizations/"
    name = "orgName"

    @classmethod
    def teardown_class(cls):
        db.Organization.drop_collection()

    # Getting empty Organizations
    def test_get_empty(self, app_client: FlaskClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when getting route with empty organizations"

    def test_get(self, app_client: FlaskClient, auth_header):
        # Manual create Organization
        o = db.Organization(organizationName=self.name)
        o.save()

        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 200
        ), "Invalid response code when getting route with organizations present"

        assert (
            len(response.json["organizations"]) == 1
        ), "Invalid payload lenght when querying organizations"

        assert (
            response.json["organizations"][0]["organizationName"] == self.name
        ), "Invalid Organization name"

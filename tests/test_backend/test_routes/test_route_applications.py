import pytest
from fastapi.testclient import TestClient

from backend.app.services import database as db


class TestGetApplications:
    endpoint = "/api/applications"
    name = "appName"

    # Getting empty Applications with no args
    def test_get_no_args(self, app_client: TestClient, auth_header):

        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 422
        ), "Invalid response code when getting Application with no args"

    # Getting created application
    @pytest.mark.asyncio
    async def test_get(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        a = db.Application(applicationName=self.name, organization=o.id)
        await a.save()
        # Done setup

        response = app_client.get(
            self.endpoint + f"?organizationID={str(o.id)}",
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting Application"

        assert (
            response.json()["applications"][0]["applicationName"] == self.name
        ), "Invalid Application name"


class TestPostApplications:
    endpoint = "/api/application"
    name = "appName"

    # Creating Application
    @pytest.mark.asyncio
    async def test_create(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        # Done setup

        response = app_client.post(
            self.endpoint,
            json={"name": self.name, "organizationID": str(o.id)},
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when posting valid data in create route"

        assert (
            app := await db.Application.find_one()
        ) and app.applicationName == self.name, "Invalid name for Application object"

    # Creating application with wrong orgID
    def test_create_with_no_org(self, app_client: TestClient, auth_header, obj_id):
        response = app_client.post(
            self.endpoint,
            json={"name": "qux", "organizationID": obj_id},
            headers=auth_header,
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when posting data to wrong orgID"

    # Creating application with same name
    @pytest.mark.asyncio
    async def test_create_invalid_name(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        a = db.Application(applicationName=self.name, organization=o.id)
        await a.save()
        # Done setup

        response = app_client.post(
            self.endpoint,
            json={"name": self.name, "organizationID": str(o.id)},
            headers=auth_header,
        )
        print(await db.Application.find_all().to_list())

        assert (
            response.status_code == 400
        ), "Invalid response code when posting data with already existing name"

    # Creating application with invalid payload
    @pytest.mark.asyncio
    async def test_create_invalid_payload(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        # Done setup

        response = app_client.post(self.endpoint, json={}, headers=auth_header)

        assert (
            response.status_code == 422
        ), "Invalid response code when posting invalid data"

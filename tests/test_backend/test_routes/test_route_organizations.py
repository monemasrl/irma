import pytest
from fastapi.testclient import TestClient

from backend.app.services import database as db


class TestPostOrganizations:
    endpoint = "/api/organization"
    name = "orgName"

    # Creating Organization
    @pytest.mark.asyncio
    async def test_create(self, app_client: TestClient, auth_header):
        response = app_client.post(
            self.endpoint,
            json={"name": self.name},
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when posting valid data"

        assert (
            len(await db.Organization.find_all().to_list()) == 1
        ), "Create organization doesn't persist in the database"

        assert (
            org := await db.Organization.find_one()
        ) and org.organizationName == self.name, "Invalid organization name"

    # Creating Organization with already used name
    @pytest.mark.asyncio
    async def test_create_invalid_name(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName=self.name)
        await o.save()
        # Done setup

        response = app_client.post(
            self.endpoint, json={"name": self.name}, headers=auth_header
        )

        assert (
            response.status_code == 400
        ), "Invalid response code when posting data with name already in use"

    # Creating organization with invalid payload
    def test_create_invalid_payload(self, app_client: TestClient, auth_header):
        response = app_client.post(self.endpoint, json={}, headers=auth_header)

        assert (
            response.status_code == 422
        ), "Invalid response code when posting an invalid payload when creating an organization"


class TestGetOrganizations:
    endpoint = "/api/organizations"
    name = "orgName"

    @pytest.mark.asyncio
    async def test_get(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName=self.name)
        await o.save()
        # Done setup

        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 200
        ), "Invalid response code when getting route with organizations present"

        assert (
            len(response.json()["organizations"]) == 1
        ), "Invalid payload lenght when querying organizations"

        assert (
            response.json()["organizations"][0]["organizationName"] == self.name
        ), "Invalid Organization name"

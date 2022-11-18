import pytest
from fastapi.testclient import TestClient

from microservice_websocket.app.services.database import User, user_manager


class TestGetUserList:
    endpoint = "/api/users"

    @pytest.mark.asyncio
    async def test_get_user_list(self, app_client: TestClient, auth_header):
        await user_manager.create_user("foo", "bar")
        await user_manager.create_user("baz", "qux")

        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 200 and len(response.json()["users"]) == 3
        ), "Invalid response when trying to get user list"


class TestGetUserInfo:
    endpoint = "/api/user/"

    def test_get_non_existing_user(self, app_client: TestClient, auth_header, obj_id):
        response = app_client.get(self.endpoint + obj_id, headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to get non existing user info"

    @pytest.mark.asyncio
    async def test_get_user_info(self, app_client: TestClient, auth_header):
        await user_manager.create_user("bar", "baz")
        user = await user_manager.get_user_from_mail("bar")
        assert user

        response = app_client.get(self.endpoint + str(user.id), headers=auth_header)

        assert response.status_code == 200 and response.json() == {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }, "Invalid response when trying to get user info"


class TestCreateUser:
    endpoint = "/api/user"

    # Test creating user with invalid payloa
    def test_create_user_invalid_payload(self, app_client: TestClient, auth_header):
        response = app_client.post(self.endpoint, json={}, headers=auth_header)

        assert (
            response.status_code == 422
        ), "Invalid response code when trying to create user\
            with invalid payload"

    @pytest.mark.asyncio
    async def test_create_user_already_existing(
        self, app_client: TestClient, auth_header
    ):
        await user_manager.create_user("foo", "qux")

        response = app_client.post(
            self.endpoint,
            json={"email": "foo", "password": "bar", "role": "standard"},
            headers=auth_header,
        )

        assert (
            response.status_code == 400
        ), "Invalid response when trying to create already existing user"

    @pytest.mark.asyncio
    async def test_create_user(self, app_client: TestClient, auth_header):
        response = app_client.post(
            self.endpoint,
            json={"email": "pippo", "password": "pluto", "role": "standard"},
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to create user with valid payload"

        assert (
            len(await User.find(User.email == "pippo").to_list()) == 1
        ), "Invalid number of User with email='pippo'"


class TestUpdateUser:
    endpoint = "/api/user/"

    def test_update_non_existing_user(
        self, app_client: TestClient, auth_header, obj_id
    ):
        response = app_client.put(
            self.endpoint + obj_id,
            json={
                "email": "foo",
                "newPassword": "bar",
                "oldPassword": "baz",
                "role": "admin",
            },
            headers=auth_header,
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to update non existing user"

    @pytest.mark.asyncio
    async def test_update_user(self, app_client: TestClient, auth_header):
        await user_manager.create_user("foo", "baz", role="standard")
        user = await user_manager.get_user_from_mail("foo")
        assert user

        response = app_client.put(
            self.endpoint + str(user.id),
            json={
                "email": "foo",
                "new_password": "bar",
                "old_password": "baz",
                "role": "admin",
            },
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to update user"

        assert (
            user := await User.find(User.email == "foo").first_or_none()
        ) and user_manager.verify_password(
            "bar", user.hashed_password
        ), "Password didn't change"

        assert (
            user := await User.find(User.email == "foo").first_or_none()
        ) and user.role == "admin", "Role didn't change"


class TestDeleteUser:
    endpoint = "/api/user/"

    def test_delete_non_existing_user(
        self, app_client: TestClient, auth_header, obj_id
    ):
        response = app_client.delete(self.endpoint + obj_id, headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to delete non existing user"

    @pytest.mark.asyncio
    async def test_delete_user(self, app_client: TestClient, auth_header):
        await user_manager.create_user("foo", "bar")
        user = await user_manager.get_user_from_mail("foo")
        assert user

        response = app_client.delete(self.endpoint + str(user.id), headers=auth_header)

        assert response.status_code == 200, "Invalid response code when deleting user"
        assert (
            len(await User.find_all().to_list()) == 1
        ), "Invalid number of users in db"

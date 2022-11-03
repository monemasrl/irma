from flask.testing import FlaskClient

from microservice_websocket.app.services.database import User, user_manager


class TestGetUserList:
    endpoint = "/api/user/list"

    @classmethod
    def teardown_class(cls):
        for user in User.objects():
            if user["email"] != "bettarini@monema.it":
                user.delete()

    def test_get_user_list(self, app_client: FlaskClient, auth_header):
        user_manager.create_user("foo", "bar")
        user_manager.create_user("baz", "qux")

        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 200
            and response.json
            and len(response.json["users"]) == 3
        ), "Invalid response when trying to get user list"


class TestGetUserInfo:
    endpoint = "/api/user/"

    @classmethod
    def teardown_class(cls):
        for user in User.objects():
            if user["email"] != "bettarini@monema.it":
                user.delete()

    def test_get_non_existing_user(self, app_client: FlaskClient, auth_header, obj_id):
        response = app_client.get(self.endpoint + obj_id, headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to get non existing user info"

    def test_get_user_info(self, app_client: FlaskClient, auth_header):
        user_manager.create_user("bar", "baz")
        user = user_manager.get_user("bar")
        assert user

        response = app_client.get(self.endpoint + str(user["id"]), headers=auth_header)

        assert (
            response.status_code == 200
            and response.json
            and response.json == user.serialize()
        ), "Invalid response when trying to get user info"


class TestCreateUser:
    endpoint = "/api/user/create"

    @classmethod
    def teardown_class(cls):
        for user in User.objects():
            if user["email"] != "bettarini@monema.it":
                user.delete()

    # Test creating user with invalid payloa
    def test_create_user_invalid_payload(self, app_client: FlaskClient, auth_header):
        response = app_client.post(self.endpoint, json={}, headers=auth_header)

        assert (
            response.status_code == 400
        ), "Invalid response code when trying to create user\
            with invalid payload"

    def test_create_user_already_existing(self, app_client: FlaskClient, auth_header):
        user_manager.create_user("foo", "qux")

        response = app_client.post(
            self.endpoint,
            json={"email": "foo", "password": "bar", "role": "standard"},
            headers=auth_header,
        )

        assert (
            response.status_code == 400
            and response.json
            and response.json["msg"] == "Already Existing User"
        ), "Invalid response when trying to create already existing user"

    def test_create_user(self, app_client: FlaskClient, auth_header):
        response = app_client.post(
            self.endpoint,
            json={"email": "pippo", "password": "pluto", "role": "standard"},
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to create user with valid payload"

        assert (
            len(User.objects(email="pippo")) == 1
        ), "Invalid number of User with email='pippo'"


class TestUpdateUser:
    endpoint = "/api/user/"

    @classmethod
    def teardown_class(cls):
        for user in User.objects():
            if user["email"] != "bettarini@monema.it":
                user.delete()

    def test_update_user_invalid_paylaod(
        self, app_client: FlaskClient, auth_header, obj_id
    ):
        response = app_client.put(self.endpoint + obj_id, json={}, headers=auth_header)

        assert (
            response.status_code == 400
        ), "Invalid response code when trying to update user with invalid payload"

    def test_update_non_existing_user(
        self, app_client: FlaskClient, auth_header, obj_id
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

    def test_update_user(self, app_client: FlaskClient, auth_header):
        user_manager.create_user("foo", "baz", role="standard")
        user = user_manager.get_user("foo")
        assert user

        response = app_client.put(
            self.endpoint + str(user["id"]),
            json={
                "email": "foo",
                "newPassword": "bar",
                "oldPassword": "baz",
                "role": "admin",
            },
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to update user"

        assert user_manager.verify(
            User.objects(email="foo").first(), "bar"
        ), "Password didn't change"

        assert (
            User.objects(email="foo").first()["role"] == "admin"
        ), "Role didn't change"


class TestDeleteUser:
    endpoint = "/api/user/"

    def test_delete_non_existing_user(
        self, app_client: FlaskClient, auth_header, obj_id
    ):
        response = app_client.delete(self.endpoint + obj_id, headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to delete non existing user"

    def test_delete_user(self, app_client: FlaskClient, auth_header):
        user_manager.create_user("foo", "bar")
        user = user_manager.get_user("foo")
        assert user

        response = app_client.delete(
            self.endpoint + str(user["id"]), headers=auth_header
        )

        assert response.status_code == 200, "Invalid response code when deleting user"
        assert len(User.objects()) == 1, "Invalid number of users in db"

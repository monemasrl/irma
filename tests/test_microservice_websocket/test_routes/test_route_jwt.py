from flask.testing import FlaskClient


class TestJwtDecorator:
    # Test decorator
    def test_jwt_no_header(self, app_client: FlaskClient):
        response = app_client.get("/test/jwt-test")

        assert (
            response.status_code == 401
        ), "Invalid response code when trying to access protected route without Auth header"

    def test_jwt(self, app_client: FlaskClient, auth_header):
        response = app_client.get("/test/jwt-test", headers=auth_header)

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to access protected route with Auth header"


class TestJwtAuthentication:
    endpoint = "/api/jwt/authenticate"

    # Trying to authenticate with invalid payload
    def test_auth_invalid_payload(self, app_client: FlaskClient):
        response = app_client.post(self.endpoint, json={})

        assert (
            response.status_code == 400
        ), "Invalid response code when trying to authenticate with invalid payload"

    # Trying to authenticate as a non-registered user
    def test_auth_non_registered(self, app_client: FlaskClient):
        response = app_client.post(
            self.endpoint, json={"username": "foo", "password": "bar"}
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to authenticate as a non-registered user"

    # Trying to authenticate with wrong password
    def test_auth_wrong_password(self, app_client: FlaskClient):
        response = app_client.post(
            self.endpoint, json={"username": "bettarini@monema.it", "password": "foo"}
        )

        assert (
            response.status_code == 401
        ), "Invalid response code when trying to authenticate with wrong password"

    # Normal authentication
    def test_auth(self, app_client: FlaskClient):
        response = app_client.post(
            self.endpoint,
            json={"username": "bettarini@monema.it", "password": "password"},
        )

        assert (
            response.status_code == 200
            and "access_token" in response.json
            and "refresh_token" in response.json
        ), "Invalid response when posting valid data"


class TestJwtRefresh:
    endpoint = "/api/jwt/refresh"

    def test_refresh(self, app_client: FlaskClient, refresh_header):
        response = app_client.post(self.endpoint, headers=refresh_header)

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to renew jwt token"

        assert (
            "access_token" in response.json
        ), "Invalid response when trying to renew jwt token"

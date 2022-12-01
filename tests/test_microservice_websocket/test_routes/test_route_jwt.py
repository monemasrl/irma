from fastapi.testclient import TestClient


class TestJwtAuth:
    endpoint = "/test/jwt-test"
    # Test decorator

    def test_jwt_no_header(self, app_client: TestClient):
        response = app_client.get(self.endpoint)

        assert (
            response.status_code == 401
        ), "Invalid response code when trying to access protected route without Auth header"

    def test_jwt(self, app_client: TestClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 200
            and response.json()["message"] == "Hi foo@bar.com"
        ), "Invalid response when trying to access protected route with Auth header"


class TestJwtAuthentication:
    endpoint = "/api/jwt/"

    # Trying to authenticate with invalid payload
    def test_auth_invalid_payload(self, app_client: TestClient):
        response = app_client.post(self.endpoint, json={})

        assert (
            response.status_code == 422
        ), "Invalid response code when trying to authenticate with invalid payload"

    # Trying to authenticate as a non-registered user
    def test_auth_non_registered(self, app_client: TestClient):
        response = app_client.post(
            self.endpoint, json={"email": "foo", "password": "bar"}
        )

        assert (
            response.status_code == 401
        ), "Invalid response code when trying to authenticate as a non-registered user"

    # Trying to authenticate with wrong password
    def test_auth_wrong_password(self, app_client: TestClient):
        response = app_client.post(
            self.endpoint, json={"email": "bettarini@monema.it", "password": "foo"}
        )

        assert (
            response.status_code == 401
        ), "Invalid response code when trying to authenticate with wrong password"

    # Normal authentication
    def test_auth(self, app_client: TestClient):
        response = app_client.post(
            self.endpoint,
            json={"email": "foo@bar.com", "password": "baz"},
        )

        assert (
            response.status_code == 200 and "access_token" in response.json()
        ), "Invalid response when posting valid data"


# class TestJwtRefresh:
#     endpoint = "/api/jwt/refresh"
#
#     def test_refresh(self, app_client: TestClient, refresh_header):
#         response = app_client.post(self.endpoint, headers=refresh_header)
#
#         assert (
#             response.status_code == 200
#         ), "Invalid response code when trying to renew jwt token"
#
#         assert (
#             "access_token" in response.json()
#         ), "Invalid response when trying to renew jwt token"

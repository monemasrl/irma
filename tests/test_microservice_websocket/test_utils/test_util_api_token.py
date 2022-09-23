from flask.testing import FlaskClient
from mock import mock_open, patch


class TestApiToken:
    endpoint = "/test/api-token-test"

    def test_decorator_no_auth_header(self, app_client: FlaskClient):
        response = app_client.get(self.endpoint)

        assert (
            response.status_code == 401
        ), "Invalid response code from route protected with @api_token_required"

    def test_decorator_wrong_header(self, app_client: FlaskClient):
        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.get(
                self.endpoint, headers={"Authorization": "Bearer 5678"}
            )

        assert (
            response.status_code == 401
        ), "Invalid response code from route protected with @api_token_required"

    def test_decorator(self, app_client: FlaskClient):
        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.get(
                self.endpoint, headers={"Authorization": "Bearer 1234"}
            )

        assert (
            response.status_code == 200
        ), "Cannot access route protected with @api_token_required with correct api-token"

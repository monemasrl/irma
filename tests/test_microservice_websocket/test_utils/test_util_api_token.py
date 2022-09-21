from flask.testing import FlaskClient
from mock import mock_open, patch


def test_api_token_decorator(app_client: FlaskClient):
    endpoint = "/test/api-token-test"

    response = app_client.get(endpoint)

    assert (
        response.status_code == 401
    ), "Invalid response code from route protected with @api_token_required"

    with patch("builtins.open", mock_open(read_data="1234")):
        response = app_client.get(endpoint, headers={"Authorization": "Bearer 1234"})

    assert (
        response.status_code == 200
    ), "Cannot access route protected with @api_token_required with correct api-token"

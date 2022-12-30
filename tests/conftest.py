import pytest
from fastapi.testclient import TestClient
from mock import patch

from backend.app.blueprints.api.test import test_router


@pytest.fixture
def app_client() -> TestClient:
    with patch("backend.app.config.TESTING", True):

        from backend.app import app

        app.include_router(test_router)
        with TestClient(app) as client:
            return client


@pytest.fixture
def token(app_client: TestClient) -> str:
    response = app_client.post(
        "/api/jwt/",
        json={"email": "foo@bar.com", "password": "baz"},
    )

    decoded_json = response.json()

    return decoded_json["access_token"]


@pytest.fixture()
def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def obj_id() -> str:
    return "63186eab0ca2d54a5c258384"


@pytest.fixture()
def sensor_data() -> dict:
    return {"foo": "bar", "baz": "qux"}

from microservice_websocket import downlink_microservice
from flask import Flask
from flask.testing import FlaskClient
import pytest

class TestFlaskApp:

    @pytest.fixture()
    def app(self) -> Flask: # type: ignore
        app = downlink_microservice.create_app()
        app.config.update({
            "TESTING": True,
        })
        # set up
        yield app
        # clean up
    
    @pytest.fixture()
    def client(self, app: Flask) -> FlaskClient:
        return app.test_client()

    # def test_main_route_get(self, client):
    #     response = client.get("/")
    #     print(response.data)
    #     assert False
    # TODO: implement testing for mqtt lib

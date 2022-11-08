from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from microservice_websocket.app.services import database as db
from microservice_websocket.app.utils.enums import NodeState


class TestGetNodes:
    endpoint = "/api/nodes/"
    name = "nodeName"

    # Getting nodes with no args
    def test_get_no_args(self, app_client: TestClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 422
        ), "Invalid response code when getting node with no args"

    @pytest.mark.asyncio
    async def test_get(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="foo")
        await o.save()
        a = db.Application(applicationName="bar", organization=o.id)
        await a.save()
        # Done setup

        # Manually create node
        n = db.Node(
            nodeID=123,
            nodeName=self.name,
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await n.save()

        # Getting newly created node
        response = app_client.get(
            self.endpoint + f"?applicationID={str(a.id)}",
            headers=auth_header,
        )

        assert response.status_code == 200, "Invalid response code when getting nodes"

        assert response.json()["nodes"][0]["nodeName"] == self.name

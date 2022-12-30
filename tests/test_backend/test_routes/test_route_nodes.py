from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from backend.app.models.node_settings import DetectorSettings, SensorSettings
from backend.app.services import database as db
from backend.app.utils.enums import NodeState


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


class TestGetSettings:
    def endpoint(self, nodeID: int):
        return f"/api/node/{nodeID}/settings"

    @pytest.mark.asyncio
    async def test_get(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="foo")
        await o.save()
        a = db.Application(applicationName="bar", organization=o.id)
        await a.save()
        n = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await n.save()
        settings = db.NodeSettings(
            node=n.id,
            d1=DetectorSettings(
                s1=SensorSettings(
                    hv=1,
                    w1_low=1,
                    w1_high=2,
                    w2_low=3,
                    w2_high=4,
                    w3_low=5,
                    w3_high=6,
                ),
                s2=SensorSettings(
                    hv=1,
                    w1_low=6,
                    w1_high=5,
                    w2_low=4,
                    w2_high=3,
                    w3_low=2,
                    w3_high=1,
                ),
            ),
            d2=DetectorSettings(
                s1=SensorSettings(
                    hv=2,
                    w1_low=2,
                    w1_high=4,
                    w2_low=6,
                    w2_high=8,
                    w3_low=10,
                    w3_high=12,
                ),
                s2=SensorSettings(
                    hv=2,
                    w1_low=12,
                    w1_high=10,
                    w2_low=8,
                    w2_high=6,
                    w3_low=4,
                    w3_high=2,
                ),
            ),
            d3=DetectorSettings(
                s1=SensorSettings(
                    hv=3,
                    w1_low=3,
                    w1_high=6,
                    w2_low=9,
                    w2_high=12,
                    w3_low=15,
                    w3_high=18,
                ),
                s2=SensorSettings(
                    hv=3,
                    w1_low=18,
                    w1_high=15,
                    w2_low=12,
                    w2_high=9,
                    w3_low=6,
                    w3_high=3,
                ),
            ),
            d4=DetectorSettings(
                s1=SensorSettings(
                    hv=4,
                    w1_low=4,
                    w1_high=8,
                    w2_low=12,
                    w2_high=16,
                    w3_low=20,
                    w3_high=24,
                ),
                s2=SensorSettings(
                    hv=4,
                    w1_low=24,
                    w1_high=20,
                    w2_low=16,
                    w2_high=12,
                    w3_low=8,
                    w3_high=4,
                ),
            ),
        )
        await settings.save()
        # Done setup

        response = app_client.get(self.endpoint(n.nodeID), headers=auth_header)

        assert (
            response.status_code == 200
        ), "Invalid response code when gettings node settings"

        assert response.json() == settings.serialize()


class TestUpdateSettings:
    def endpoint(self, nodeID: int):
        return f"/api/node/{nodeID}/settings"

    def test_update_non_existing_node(self, app_client: TestClient, auth_header):
        payload = {
            "d4": {
                "s1": {
                    "hv": 1,
                    "w1_low": 1,
                    "w1_high": 2,
                    "w2_low": 3,
                    "w2_high": 4,
                    "w3_low": 5,
                    "w3_high": 6,
                },
                "s2": {
                    "hv": 1,
                    "w1_low": 6,
                    "w1_high": 5,
                    "w2_low": 4,
                    "w2_high": 3,
                    "w3_low": 2,
                    "w3_high": 1,
                },
            },
            "d3": {
                "s1": {
                    "hv": 2,
                    "w1_low": 2,
                    "w1_high": 4,
                    "w2_low": 6,
                    "w2_high": 8,
                    "w3_low": 10,
                    "w3_high": 12,
                },
                "s2": {
                    "hv": 2,
                    "w1_low": 12,
                    "w1_high": 10,
                    "w2_low": 8,
                    "w2_high": 6,
                    "w3_low": 4,
                    "w3_high": 2,
                },
            },
            "d2": {
                "s1": {
                    "hv": 3,
                    "w1_low": 3,
                    "w1_high": 6,
                    "w2_low": 9,
                    "w2_high": 12,
                    "w3_low": 15,
                    "w3_high": 18,
                },
                "s2": {
                    "hv": 3,
                    "w1_low": 18,
                    "w1_high": 15,
                    "w2_low": 12,
                    "w2_high": 9,
                    "w3_low": 6,
                    "w3_high": 3,
                },
            },
            "d1": {
                "s1": {
                    "hv": 4,
                    "w1_low": 4,
                    "w1_high": 8,
                    "w2_low": 12,
                    "w2_high": 16,
                    "w3_low": 20,
                    "w3_high": 24,
                },
                "s2": {
                    "hv": 4,
                    "w1_low": 24,
                    "w1_high": 20,
                    "w2_low": 16,
                    "w2_high": 12,
                    "w3_low": 8,
                    "w3_high": 4,
                },
            },
        }

        response = app_client.put(self.endpoint(123), json=payload, headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when updating settings of non-extisting node"

    @pytest.mark.asyncio
    async def test_update_non_existing_settings(
        self, app_client: TestClient, auth_header
    ):
        o = db.Organization(organizationName="foo")
        await o.save()
        a = db.Application(applicationName="bar", organization=o.id)
        await a.save()
        n = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await n.save()
        # Done setup

        payload = {
            "d1": {
                "s1": {
                    "hv": 1,
                    "w1_low": 1,
                    "w1_high": 2,
                    "w2_low": 3,
                    "w2_high": 4,
                    "w3_low": 5,
                    "w3_high": 6,
                },
                "s2": {
                    "hv": 1,
                    "w1_low": 6,
                    "w1_high": 5,
                    "w2_low": 4,
                    "w2_high": 3,
                    "w3_low": 2,
                    "w3_high": 1,
                },
            },
            "d2": {
                "s1": {
                    "hv": 2,
                    "w1_low": 2,
                    "w1_high": 4,
                    "w2_low": 6,
                    "w2_high": 8,
                    "w3_low": 10,
                    "w3_high": 12,
                },
                "s2": {
                    "hv": 2,
                    "w1_low": 12,
                    "w1_high": 10,
                    "w2_low": 8,
                    "w2_high": 6,
                    "w3_low": 4,
                    "w3_high": 2,
                },
            },
            "d3": {
                "s1": {
                    "hv": 3,
                    "w1_low": 3,
                    "w1_high": 6,
                    "w2_low": 9,
                    "w2_high": 12,
                    "w3_low": 15,
                    "w3_high": 18,
                },
                "s2": {
                    "hv": 3,
                    "w1_low": 18,
                    "w1_high": 15,
                    "w2_low": 12,
                    "w2_high": 9,
                    "w3_low": 6,
                    "w3_high": 3,
                },
            },
            "d4": {
                "s1": {
                    "hv": 4,
                    "w1_low": 4,
                    "w1_high": 8,
                    "w2_low": 12,
                    "w2_high": 16,
                    "w3_low": 20,
                    "w3_high": 24,
                },
                "s2": {
                    "hv": 4,
                    "w1_low": 24,
                    "w1_high": 20,
                    "w2_low": 16,
                    "w2_high": 12,
                    "w3_low": 8,
                    "w3_high": 4,
                },
            },
        }

        response = app_client.put(
            self.endpoint(n.nodeID), json=payload, headers=auth_header
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to update non-existing settings"

        assert (
            len(await db.NodeSettings.find_all().to_list()) == 1
        ), "Invalid number of settings"

        assert (
            settings := await db.NodeSettings.find_one()
        ) and settings.serialize() == payload, "Invalid settings in database"

    @pytest.mark.asyncio
    async def test_update_settings(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="foo")
        await o.save()
        a = db.Application(applicationName="bar", organization=o.id)
        await a.save()
        n = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await n.save()
        settings = db.NodeSettings(
            node=n.id,
            d1=DetectorSettings(
                s1=SensorSettings(
                    hv=1,
                    w1_low=1,
                    w1_high=2,
                    w2_low=3,
                    w2_high=4,
                    w3_low=5,
                    w3_high=6,
                ),
                s2=SensorSettings(
                    hv=1,
                    w1_low=6,
                    w1_high=5,
                    w2_low=4,
                    w2_high=3,
                    w3_low=2,
                    w3_high=1,
                ),
            ),
            d2=DetectorSettings(
                s1=SensorSettings(
                    hv=2,
                    w1_low=2,
                    w1_high=4,
                    w2_low=6,
                    w2_high=8,
                    w3_low=10,
                    w3_high=12,
                ),
                s2=SensorSettings(
                    hv=2,
                    w1_low=12,
                    w1_high=10,
                    w2_low=8,
                    w2_high=6,
                    w3_low=4,
                    w3_high=2,
                ),
            ),
            d3=DetectorSettings(
                s1=SensorSettings(
                    hv=3,
                    w1_low=3,
                    w1_high=6,
                    w2_low=9,
                    w2_high=12,
                    w3_low=15,
                    w3_high=18,
                ),
                s2=SensorSettings(
                    hv=3,
                    w1_low=18,
                    w1_high=15,
                    w2_low=12,
                    w2_high=9,
                    w3_low=6,
                    w3_high=3,
                ),
            ),
            d4=DetectorSettings(
                s1=SensorSettings(
                    hv=4,
                    w1_low=4,
                    w1_high=8,
                    w2_low=12,
                    w2_high=16,
                    w3_low=20,
                    w3_high=24,
                ),
                s2=SensorSettings(
                    hv=4,
                    w1_low=24,
                    w1_high=20,
                    w2_low=16,
                    w2_high=12,
                    w3_low=8,
                    w3_high=4,
                ),
            ),
        )
        await settings.save()
        # Done setup

        payload = {
            "d4": {
                "s1": {
                    "hv": 1,
                    "w1_low": 1,
                    "w1_high": 2,
                    "w2_low": 3,
                    "w2_high": 4,
                    "w3_low": 5,
                    "w3_high": 6,
                },
                "s2": {
                    "hv": 1,
                    "w1_low": 6,
                    "w1_high": 5,
                    "w2_low": 4,
                    "w2_high": 3,
                    "w3_low": 2,
                    "w3_high": 1,
                },
            },
            "d3": {
                "s1": {
                    "hv": 2,
                    "w1_low": 2,
                    "w1_high": 4,
                    "w2_low": 6,
                    "w2_high": 8,
                    "w3_low": 10,
                    "w3_high": 12,
                },
                "s2": {
                    "hv": 2,
                    "w1_low": 12,
                    "w1_high": 10,
                    "w2_low": 8,
                    "w2_high": 6,
                    "w3_low": 4,
                    "w3_high": 2,
                },
            },
            "d2": {
                "s1": {
                    "hv": 3,
                    "w1_low": 3,
                    "w1_high": 6,
                    "w2_low": 9,
                    "w2_high": 12,
                    "w3_low": 15,
                    "w3_high": 18,
                },
                "s2": {
                    "hv": 3,
                    "w1_low": 18,
                    "w1_high": 15,
                    "w2_low": 12,
                    "w2_high": 9,
                    "w3_low": 6,
                    "w3_high": 3,
                },
            },
            "d1": {
                "s1": {
                    "hv": 4,
                    "w1_low": 4,
                    "w1_high": 8,
                    "w2_low": 12,
                    "w2_high": 16,
                    "w3_low": 20,
                    "w3_high": 24,
                },
                "s2": {
                    "hv": 4,
                    "w1_low": 24,
                    "w1_high": 20,
                    "w2_low": 16,
                    "w2_high": 12,
                    "w3_low": 8,
                    "w3_high": 4,
                },
            },
        }

        from mock import patch

        with patch("backend.app.config.TESTING", True):
            response = app_client.put(
                self.endpoint(n.nodeID), json=payload, headers=auth_header
            )

        assert (
            response.status_code == 200
        ), "Invalid response code when updating node settings"

        assert (
            len(await db.NodeSettings.find_all().to_list()) == 1
        ), "Invalid number of NodeSettings"

        assert (
            settings := await db.NodeSettings.find_one()
        ) and settings.serialize() == payload, "Invalid settings in database"

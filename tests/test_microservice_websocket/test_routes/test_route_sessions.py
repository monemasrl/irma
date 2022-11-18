from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from microservice_websocket.app.services import database as db
from microservice_websocket.app.services.database.models import NodeState


class TestGetSessions:
    endpoint = "/api/session"

    # Get without args
    def test_get_no_args(self, app_client: TestClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 422
        ), "Invalid response code when getting sessions with no nodeID"

    # Get session of non existing node
    def test_get_non_existing_node(self, app_client: TestClient, auth_header):
        response = app_client.get(self.endpoint + "?nodeID=100", headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to get session of non existing node"

    # Get whene there's no session
    @pytest.mark.asyncio
    async def test_get_no_session(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        a = db.Application(applicationName="appName", organization=o.id)
        await a.save()
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await node.save()
        # Done setup

        response = app_client.get(self.endpoint + "?nodeID=123", headers=auth_header)

        assert (
            response.status_code == 200
        ), "Invalid response code when getting session from valid node"

        assert len(response.json()["readings"]) == 0, "Invalid readings length"

    # Get the latest session
    @pytest.mark.asyncio
    async def test_get_latest_session(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        a = db.Application(applicationName="appName", organization=o.id)
        await a.save()
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await node.save()
        r1 = db.Reading(
            node=node.id,
            canID=1,
            sensorNumber=1,
            readingID=1,
            sessionID=1,
            publishedAt=datetime.now(),
        )
        await r1.save()
        r2 = db.Reading(
            node=node.id,
            canID=2,
            sensorNumber=1,
            readingID=1,
            sessionID=2,
            publishedAt=datetime.now(),
        )
        await r2.save()
        r3 = db.Reading(
            node=node.id,
            canID=3,
            sensorNumber=1,
            readingID=1,
            sessionID=3,
            publishedAt=datetime.now(),
        )
        await r3.save()
        # Done setup

        response = app_client.get(
            self.endpoint + f"?nodeID={str(node.nodeID)}",
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when querying latest session"

        assert (
            response.json()["readings"][0]["canID"] == 3
        ), "Invalid response when querying latest session"

    @pytest.mark.asyncio
    async def test_get_specific_session(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        a = db.Application(applicationName="appName", organization=o.id)
        await a.save()
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await node.save()
        r1 = db.Reading(
            node=node.id,
            canID=1,
            sensorNumber=1,
            readingID=1,
            sessionID=1,
            publishedAt=datetime.now(),
        )
        await r1.save()
        r2 = db.Reading(
            node=node.id,
            canID=2,
            sensorNumber=1,
            readingID=1,
            sessionID=2,
            publishedAt=datetime.now(),
        )
        await r2.save()
        r3 = db.Reading(
            node=node.id,
            canID=3,
            sensorNumber=1,
            readingID=1,
            sessionID=3,
            publishedAt=datetime.now(),
        )
        await r3.save()
        # Done setup

        response = app_client.get(
            self.endpoint + f"/2?nodeID={str(node.nodeID)}",
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when querying specific session"

        assert (
            response.json()["readings"][0]["canID"] == 2
        ), "Invalid response when querying specific session"


class TestGetSessionID:
    endpoint = "/api/sessions"

    # Get sessionIDs without args
    def test_get_no_args(self, app_client: TestClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 422
        ), "Invalid response code when submitting no args"

    # Get sessionIDs of non existings node
    def test_get_non_existing_node(self, app_client: TestClient, auth_header):
        response = app_client.get(self.endpoint + "?nodeID=100", headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when getting sessionIDs of non existring Node"

    # Get sessionIDs with no readings
    @pytest.mark.asyncio
    async def test_get_no_ids(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        a = db.Application(applicationName="appName", organization=o.id)
        await a.save()
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await node.save()
        # Done setup

        response = app_client.get(
            self.endpoint + f"?nodeID={str(node.nodeID)}",
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting sessionIDs from valid Node"

        assert (
            len(response.json()["IDs"]) == 0
        ), "Invalid response when getting sessionIDs from valid Node"

    # Get sessionIDs
    @pytest.mark.asyncio
    async def test_get(self, app_client: TestClient, auth_header):
        o = db.Organization(organizationName="orgName")
        await o.save()
        a = db.Application(applicationName="appName", organization=o.id)
        await a.save()
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=a.id,
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        await node.save()
        r1 = db.Reading(
            node=node.id,
            canID=1,
            sensorNumber=1,
            readingID=1,
            sessionID=1,
            publishedAt=datetime.now(),
        )
        await r1.save()
        r2 = db.Reading(
            node=node.id,
            canID=2,
            sensorNumber=1,
            readingID=1,
            sessionID=2,
            publishedAt=datetime.now(),
        )
        await r2.save()
        # Done setup

        response = app_client.get(
            self.endpoint + f"?nodeID={str(node.nodeID)}",
            headers=auth_header,
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting sessionIDs from valid Node"

        assert (
            len(response.json()["IDs"]) == 2
        ), "Invalid response when getting sessionIDs from valid Node"

from fastapi.testclient import TestClient

from microservice_websocket.app.utils.external_archiviation import SET_NAME


class TestGetExternalArchiviation:
    endpoint = "/api/external-archiviations"

    # Test get external archiviations endopoints
    def test_get_data(self, app_client: TestClient, auth_header):
        from microservice_websocket.app import redis_client

        mock_endpoint = "foobar"
        redis_client.sadd(SET_NAME, mock_endpoint)

        response = app_client.get(self.endpoint, headers=auth_header)

        assert response.status_code == 200, "Invalid response code when querying data"
        assert len(response.json()["endpoints"]) == 1, "Invalid endpoints number"
        assert response.json()["endpoints"][0] == mock_endpoint, "Invalid endpoint"

        redis_client.srem(SET_NAME, mock_endpoint)


class TestPostExternalArchiviation:
    endpoint = "/api/external-archiviation"

    # Test adding url of external archiviation adapter
    # with wrong payload
    def test_add_invalid_payload(self, app_client: TestClient, auth_header):
        response = app_client.post(
            self.endpoint,
            headers=auth_header,
            json={},
        )

        assert (
            response.status_code == 422
        ), "Invalid response code when posting invalid data"

    # Test adding url of external archiviation adapter
    def test_add(self, app_client: TestClient, auth_header):
        from microservice_websocket.app import redis_client

        mock_endpoint = "localhost:8080"
        response = app_client.post(
            self.endpoint,
            headers=auth_header,
            json={"endpoint": mock_endpoint},
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when posting valid data"
        assert len(redis_client.smembers(SET_NAME)) == 1, "Invalid number of endpoints"
        assert redis_client.sismember(SET_NAME, mock_endpoint)

        redis_client.srem(SET_NAME, mock_endpoint)


class TestDeleteExternalArchiviation:
    endpoint = "/api/external-archiviation/"

    # Test deleting non-existing endpoint of external archiviation adapter
    def test_delete_non_existing_endpoint(self, app_client: TestClient, auth_header):
        response = app_client.delete(self.endpoint + "foobar", headers=auth_header)

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to delete non-existing endpoint"

    # Test deleting the endpoint of external archiviation adapter
    def test_delete(self, app_client: TestClient, auth_header):
        from microservice_websocket.app import redis_client

        mock_endpoint = "bazqux"
        redis_client.sadd(SET_NAME, mock_endpoint)

        response = app_client.delete(self.endpoint + mock_endpoint, headers=auth_header)

        assert (
            response.status_code == 200
        ), "Invalid response code when trying to delete endpoint"
        assert (
            len(redis_client.smembers(SET_NAME)) == 0
        ), "Invalid number of endpoints after deletion"

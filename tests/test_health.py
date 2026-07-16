"""Health endpoint for load balancers and Docker."""

from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert data["env"] == get_settings().app_env

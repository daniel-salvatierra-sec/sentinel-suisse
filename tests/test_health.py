"""Health endpoint for load balancers and Docker."""

from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings


def test_health_endpoint(client: TestClient) -> None:
    trusted_hosts = get_settings().trusted_hosts_list()
    host_header = trusted_hosts[0] if trusted_hosts else "testserver"
    response = client.get("/health", headers={"Host": host_header})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert data["env"] == get_settings().app_env

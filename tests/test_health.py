"""Health endpoint for load balancers and Docker."""

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app


def test_health_endpoint(client: TestClient) -> None:
    trusted_hosts = get_settings().trusted_hosts_list()
    host_header = trusted_hosts[0] if trusted_hosts else "testserver"
    response = client.get("/health", headers={"Host": host_header})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["env"] == get_settings().app_env


def test_health_returns_503_when_database_down(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sentinel_suisse.main.check_database", lambda: False)
    get_settings.cache_clear()
    app = create_app()
    client = TestClient(app)
    trusted_hosts = get_settings().trusted_hosts_list()
    host_header = trusted_hosts[0] if trusted_hosts else "testserver"
    response = client.get("/health", headers={"Host": host_header})
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
    assert data["database"] == "error"

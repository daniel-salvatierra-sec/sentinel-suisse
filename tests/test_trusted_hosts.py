"""TrustedHost middleware for production deployments."""

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app


@pytest.fixture
def trusted_host_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("TRUSTED_HOSTS", "allowed.example")
    get_settings.cache_clear()
    return TestClient(create_app())


def test_trusted_host_allows_configured_host(trusted_host_client: TestClient) -> None:
    response = trusted_host_client.get("/health", headers={"Host": "allowed.example"})
    assert response.status_code == 200, response.text


def test_trusted_host_blocks_unknown_host(trusted_host_client: TestClient) -> None:
    response = trusted_host_client.get("/health", headers={"Host": "evil.example"})
    assert response.status_code == 400


def test_trusted_host_disabled_without_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("TRUSTED_HOSTS", "")
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/health", headers={"Host": "anything.example"})
    assert response.status_code == 200, response.text

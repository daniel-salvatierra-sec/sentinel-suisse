"""Tests for development-only public search preview."""

import os

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import app


@pytest.fixture
def dev_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    get_settings.cache_clear()
    return TestClient(app)


@pytest.fixture
def prod_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    yield TestClient(app)
    monkeypatch.setenv("APP_ENV", os.environ.get("APP_ENV", "development"))
    get_settings.cache_clear()


def test_public_search_available_in_development(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")
    response = dev_client.get("/api/v1/public/search?listing_type=housing")
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_public_search_hidden_in_production(prod_client: TestClient) -> None:
    response = prod_client.get("/api/v1/public/search?listing_type=housing")
    assert response.status_code == 404

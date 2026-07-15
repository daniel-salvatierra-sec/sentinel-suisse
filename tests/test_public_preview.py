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


def test_public_search_enabled_flag_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("PUBLIC_SEARCH_ENABLED", "true")
    get_settings.cache_clear()
    client = TestClient(app)
    try:
        response = client.get("/api/v1/public/search?listing_type=housing")
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)
    finally:
        monkeypatch.delenv("PUBLIC_SEARCH_ENABLED", raising=False)
        monkeypatch.setenv("APP_ENV", "development")
        get_settings.cache_clear()


def test_public_search_pagination_and_price_filter(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    page = dev_client.get("/api/v1/public/search?listing_type=housing&limit=1&offset=0")
    assert page.status_code == 200, page.text
    first = page.json()
    assert isinstance(first, list)
    assert len(first) <= 1

    priced = dev_client.get(
        "/api/v1/public/search?listing_type=housing&price_min=1000&price_max=999999&limit=50"
    )
    assert priced.status_code == 200, priced.text
    for item in priced.json():
        if item.get("price") is not None:
            assert float(item["price"]) >= 1000

    bad = dev_client.get("/api/v1/public/search?listing_type=housing&price_min=5000&price_max=1000")
    assert bad.status_code == 422

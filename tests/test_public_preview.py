"""Tests for development-only public search preview."""

import os

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app


@pytest.fixture
def dev_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("TRUSTED_HOSTS", "")
    get_settings.cache_clear()
    return TestClient(create_app())


@pytest.fixture
def prod_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("TRUSTED_HOSTS", "")
    get_settings.cache_clear()
    yield TestClient(create_app())
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
    client = TestClient(create_app())
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


def test_public_search_housing_and_job_filters(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    housing = dev_client.get(
        "/api/v1/public/search?listing_type=housing"
        "&rooms_min=2.5&property_type=apartment&has_parking=true&limit=50"
    )
    assert housing.status_code == 200, housing.text
    assert isinstance(housing.json(), list)

    jobs = dev_client.get(
        "/api/v1/public/search?listing_type=job"
        "&job_category=it&employment_type=permanent"
        "&workload_min=80&workload_max=100&limit=50"
    )
    assert jobs.status_code == 200, jobs.text
    assert isinstance(jobs.json(), list)

    bad_workload = dev_client.get(
        "/api/v1/public/search?listing_type=job&workload_min=90&workload_max=40"
    )
    assert bad_workload.status_code == 422


def test_public_providers_and_provider_filter(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    providers = dev_client.get("/api/v1/public/providers")
    assert providers.status_code == 200, providers.text
    data = providers.json()
    assert isinstance(data, list)
    assert all(item.get("is_active") is True for item in data)

    if not data:
        return

    provider_id = data[0]["id"]
    filtered = dev_client.get(
        f"/api/v1/public/search?listing_type=housing&provider_id={provider_id}&limit=50"
    )
    assert filtered.status_code == 200, filtered.text
    for item in filtered.json():
        assert item["provider_id"] == provider_id

    if len(data) < 2:
        return

    id_a, id_b = data[0]["id"], data[1]["id"]
    multi = dev_client.get(
        f"/api/v1/public/search?listing_type=housing"
        f"&provider_ids={id_a}&provider_ids={id_b}&limit=50"
    )
    assert multi.status_code == 200, multi.text
    allowed = {id_a, id_b}
    for item in multi.json():
        assert item["provider_id"] in allowed

    combined = dev_client.get(
        f"/api/v1/public/search?listing_type=housing"
        f"&provider_id={id_a}&provider_ids={id_b}&limit=50"
    )
    assert combined.status_code == 200, combined.text
    for item in combined.json():
        assert item["provider_id"] in allowed


def test_public_providers_hidden_in_production(prod_client: TestClient) -> None:
    response = prod_client.get("/api/v1/public/providers")
    assert response.status_code == 404

"""Tests for public alert signup (Phase 16)."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app


def _unique_email() -> str:
    return f"signup-{uuid.uuid4().hex[:10]}@example.com"


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


def _signup_payload(email: str | None = None, *, with_phone: bool = False) -> dict:
    payload: dict = {
        "email": email or _unique_email(),
        "locale": "fr",
        "consent": True,
        "query": {"listing_type": "housing", "location": "Geneva"},
    }
    if with_phone:
        payload["phone"] = "+41791234567"
    return payload


def test_public_signup_creates_user_channels_and_search(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    payload = _signup_payload()
    response = dev_client.post("/api/v1/public/signup", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email_verified"] is True
    assert data["whatsapp_verified"] is False
    assert data["verification_pending"] is False
    api_key = data["api_key"]

    searches = dev_client.get(
        "/api/v1/saved-searches",
        headers={"X-API-Key": api_key},
    )
    assert searches.status_code == 200
    names = [item["name"] for item in searches.json()]
    assert any("Geneva" in name for name in names)

    channels = dev_client.get(
        "/api/v1/notification-channels",
        headers={"X-API-Key": api_key},
    )
    assert channels.status_code == 200
    types = {item["channel_type"] for item in channels.json()}
    assert types == {"email"}

    me = dev_client.get("/api/v1/users/me", headers={"X-API-Key": api_key})
    assert me.status_code == 200
    profile = me.json()
    assert profile["is_premium"] is False
    assert profile["saved_search_limit"] == 1
    assert profile["saved_search_count"] == 1


def test_public_signup_rejects_whatsapp_on_free(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    response = dev_client.post("/api/v1/public/signup", json=_signup_payload(with_phone=True))
    assert response.status_code == 403, response.text
    assert response.json()["detail"] == "whatsapp_requires_premium"


def test_public_signup_rejects_duplicate_email(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    email = _unique_email()
    first = dev_client.post("/api/v1/public/signup", json=_signup_payload(email))
    assert first.status_code == 201, first.text

    second = dev_client.post("/api/v1/public/signup", json=_signup_payload(email))
    assert second.status_code == 409


def test_public_signup_requires_consent(dev_client: TestClient) -> None:
    payload = _signup_payload()
    payload["consent"] = False
    response = dev_client.post("/api/v1/public/signup", json=payload)
    assert response.status_code == 422


def test_public_signup_hidden_in_production(prod_client: TestClient) -> None:
    response = prod_client.post("/api/v1/public/signup", json=_signup_payload())
    assert response.status_code == 404


def test_public_signup_enabled_flag_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("PUBLIC_SIGNUP_ENABLED", "true")
    monkeypatch.setenv("SIGNUP_AUTO_VERIFY", "true")
    get_settings.cache_clear()
    client = TestClient(create_app())
    try:
        response = client.post("/api/v1/public/signup", json=_signup_payload())
        assert response.status_code == 201, response.text
    finally:
        monkeypatch.delenv("PUBLIC_SIGNUP_ENABLED", raising=False)
        monkeypatch.delenv("SIGNUP_AUTO_VERIFY", raising=False)
        monkeypatch.setenv("APP_ENV", "development")
        get_settings.cache_clear()

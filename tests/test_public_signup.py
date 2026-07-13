"""Tests for public alert signup (Phase 16)."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import app


def _unique_email() -> str:
    return f"signup-{uuid.uuid4().hex[:10]}@example.com"


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


def _signup_payload(email: str | None = None) -> dict:
    return {
        "email": email or _unique_email(),
        "phone": "+41791234567",
        "locale": "fr",
        "consent": True,
        "query": {"listing_type": "housing", "location": "Geneva"},
    }


def test_public_signup_creates_user_channels_and_search(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    payload = _signup_payload()
    response = dev_client.post("/api/v1/public/signup", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email_verified"] is True
    assert data["whatsapp_verified"] is True
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
    assert types == {"email", "whatsapp"}


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

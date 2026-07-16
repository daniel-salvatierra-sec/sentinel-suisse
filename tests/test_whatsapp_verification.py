"""Tests for WhatsApp channel verification on signup."""

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app
from sentinel_suisse.security.verification_tokens import create_channel_verification_token


@pytest.fixture
def verification_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    secret = f"phase19-{uuid.uuid4().hex}"
    monkeypatch.setenv("SECRET_KEY", secret)
    get_settings.cache_clear()
    return secret


@pytest.fixture
def dev_client(verification_secret: str) -> TestClient:  # noqa: ARG001
    get_settings.cache_clear()
    return TestClient(create_app())


def _unique_email() -> str:
    return f"wa-verify-{uuid.uuid4().hex[:10]}@example.com"


@patch("sentinel_suisse.services.email_verification.httpx.post")
def test_signup_sends_whatsapp_verification_when_auto_verify_disabled(
    mock_post,
    dev_client: TestClient,
    verification_secret: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    monkeypatch.setenv("SIGNUP_AUTO_VERIFY", "false")
    monkeypatch.setenv("NOTIFIER_MODE", "console")
    get_settings.cache_clear()

    payload = {
        "email": _unique_email(),
        "phone": "+41791234567",
        "locale": "fr",
        "consent": True,
        "query": {"listing_type": "housing", "location": "Zurich"},
    }
    response = dev_client.post("/api/v1/public/signup", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["whatsapp_verification_sent"] is True
    assert data["whatsapp_verified"] is False

    channels = dev_client.get(
        "/api/v1/notification-channels",
        headers={"X-API-Key": data["api_key"]},
    )
    wa_channel = next(item for item in channels.json() if item["channel_type"] == "whatsapp")
    assert wa_channel["is_verified"] is False

    token = create_channel_verification_token(
        channel_id=wa_channel["id"],
        user_id=data["user_id"],
        secret=verification_secret,
        ttl_hours=24,
    )
    verify = dev_client.get(f"/api/v1/public/verify-channel?token={token}")
    assert verify.status_code == 200, verify.text
    assert verify.json()["channel_type"] == "whatsapp"

    channels_after = dev_client.get(
        "/api/v1/notification-channels",
        headers={"X-API-Key": data["api_key"]},
    )
    wa_after = next(item for item in channels_after.json() if item["channel_type"] == "whatsapp")
    assert wa_after["is_verified"] is True
    mock_post.assert_not_called()

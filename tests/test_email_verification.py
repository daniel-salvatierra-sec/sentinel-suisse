"""Tests for email verification tokens and public verify endpoint."""

import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import app
from sentinel_suisse.security.verification_tokens import (
    VerificationTokenError,
    create_channel_verification_token,
    parse_channel_verification_token,
)


@pytest.fixture
def verification_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    """Ephemeral HMAC secret for this test module (not a production credential)."""
    secret = f"phase18-{uuid.uuid4().hex}"
    monkeypatch.setenv("SECRET_KEY", secret)
    get_settings.cache_clear()
    return secret


@pytest.fixture
def dev_client(verification_secret: str) -> TestClient:  # noqa: ARG001
    return TestClient(app)


def _unique_email() -> str:
    return f"verify-{uuid.uuid4().hex[:10]}@example.com"


def test_verification_token_roundtrip(verification_secret: str) -> None:
    token = create_channel_verification_token(
        channel_id=42,
        user_id=7,
        secret=verification_secret,
        ttl_hours=24,
    )
    claims = parse_channel_verification_token(token, verification_secret)
    assert claims == {"channel_id": 42, "user_id": 7}


def test_verification_token_rejects_tampering(verification_secret: str) -> None:
    token = create_channel_verification_token(
        channel_id=1,
        user_id=1,
        secret=verification_secret,
        ttl_hours=24,
    )
    tampered = token[:-4] + "xxxx"
    with pytest.raises(VerificationTokenError):
        parse_channel_verification_token(tampered, verification_secret)


def test_signup_sends_verification_when_auto_verify_disabled(
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
        "locale": "fr",
        "consent": True,
        "query": {"listing_type": "housing", "location": "Lausanne"},
    }
    response = dev_client.post("/api/v1/public/signup", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email_verified"] is False
    assert data["verification_pending"] is True
    assert data["verification_email_sent"] is True

    channels = dev_client.get(
        "/api/v1/notification-channels",
        headers={"X-API-Key": data["api_key"]},
    )
    assert channels.status_code == 200
    email_channel = next(item for item in channels.json() if item["channel_type"] == "email")
    assert email_channel["is_verified"] is False

    token = create_channel_verification_token(
        channel_id=email_channel["id"],
        user_id=data["user_id"],
        secret=verification_secret,
        ttl_hours=24,
    )
    verify = dev_client.get(f"/api/v1/public/verify-email?token={token}")
    assert verify.status_code == 200, verify.text
    assert verify.json()["verified"] is True

    channels_after = dev_client.get(
        "/api/v1/notification-channels",
        headers={"X-API-Key": data["api_key"]},
    )
    email_after = next(item for item in channels_after.json() if item["channel_type"] == "email")
    assert email_after["is_verified"] is True


def test_verify_email_rejects_invalid_token(dev_client: TestClient) -> None:
    response = dev_client.get("/api/v1/public/verify-email?token=not-a-valid-token")
    assert response.status_code == 400

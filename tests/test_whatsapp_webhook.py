"""WhatsApp webhook challenge + signature tests (no Meta network)."""

import hashlib
import hmac
import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.main import app
from sentinel_suisse.services.whatsapp_webhook import (
    WhatsAppWebhookError,
    extract_inbound_sender_ids,
    summarize_webhook_payload,
    verify_request_signature,
    verify_subscription_challenge,
)


def _ephemeral(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def test_verify_subscription_challenge_ok() -> None:
    verify = _ephemeral("vt")
    settings = Settings().model_copy(update={"whatsapp_verify_token": verify})
    challenge = verify_subscription_challenge(
        settings,
        hub_mode="subscribe",
        hub_verify_token=verify,
        hub_challenge="12345",
    )
    assert challenge == "12345"


def test_verify_subscription_challenge_bad_token() -> None:
    verify = _ephemeral("vt")
    settings = Settings().model_copy(update={"whatsapp_verify_token": verify})
    with pytest.raises(WhatsAppWebhookError):
        verify_subscription_challenge(
            settings,
            hub_mode="subscribe",
            hub_verify_token=_ephemeral("bad"),
            hub_challenge="12345",
        )


def test_verify_request_signature_ok() -> None:
    app_key = _ephemeral("app")
    body = b'{"object":"whatsapp_business_account"}'
    digest = hmac.new(app_key.encode(), body, hashlib.sha256).hexdigest()
    settings = Settings().model_copy(update={"whatsapp_app_secret": app_key})
    verify_request_signature(
        settings,
        body=body,
        signature_header=f"sha256={digest}",
    )


def test_verify_request_signature_mismatch() -> None:
    settings = Settings().model_copy(update={"whatsapp_app_secret": _ephemeral("app")})
    with pytest.raises(WhatsAppWebhookError):
        verify_request_signature(
            settings,
            body=b"{}",
            signature_header="sha256=deadbeef",
        )


def test_summarize_webhook_payload_counts() -> None:
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [{"id": "wamid.1"}],
                            "statuses": [{"id": "wamid.1", "status": "delivered"}],
                        }
                    }
                ]
            }
        ],
    }
    summary = summarize_webhook_payload(payload)
    assert summary["object"] == "whatsapp_business_account"
    assert summary["entry_count"] == 1
    assert summary["message_count"] == 1
    assert summary["status_count"] == 1


def test_extract_inbound_sender_ids() -> None:
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [{"from": "41791234567", "id": "wamid.1", "type": "text"}]
                        }
                    }
                ]
            }
        ],
    }
    assert extract_inbound_sender_ids(payload) == ["41791234567"]


def test_webhook_get_challenge(monkeypatch: pytest.MonkeyPatch) -> None:
    verify = _ephemeral("vt")
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", verify)
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "")
    get_settings.cache_clear()
    client = TestClient(app)
    try:
        response = client.get(
            "/api/v1/webhooks/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": verify,
                "hub.challenge": "challenge-42",
            },
        )
        assert response.status_code == 200
        assert response.text == "challenge-42"
    finally:
        get_settings.cache_clear()


def test_webhook_get_rejects_bad_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", _ephemeral("vt"))
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "")
    get_settings.cache_clear()
    client = TestClient(app)
    try:
        response = client.get(
            "/api/v1/webhooks/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": _ephemeral("bad"),
                "hub.challenge": "challenge-42",
            },
        )
        assert response.status_code == 403
    finally:
        get_settings.cache_clear()


def test_webhook_post_ack_without_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", _ephemeral("vt"))
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "")
    get_settings.cache_clear()
    client = TestClient(app)
    try:
        response = client.post(
            "/api/v1/webhooks/whatsapp",
            json={"object": "whatsapp_business_account", "entry": []},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["verified"] == 0
    finally:
        get_settings.cache_clear()


def test_webhook_auto_verifies_matching_whatsapp_channel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("SIGNUP_AUTO_VERIFY", "false")
    monkeypatch.setenv("NOTIFIER_MODE", "console")
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "")
    monkeypatch.setenv("WHATSAPP_INBOUND_AUTO_VERIFY", "true")
    get_settings.cache_clear()
    client = TestClient(app)

    phone_e164 = "+41791112233"
    email = f"wa-inbound-{uuid.uuid4().hex[:10]}@example.com"
    try:
        signup = client.post(
            "/api/v1/public/signup",
            json={
                "email": email,
                "phone": phone_e164,
                "locale": "fr",
                "consent": True,
                "query": {"listing_type": "housing", "location": "Geneva"},
            },
        )
        assert signup.status_code == 201, signup.text
        api_key = signup.json()["api_key"]
        assert signup.json()["whatsapp_verified"] is False

        inbound = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "41791112233",
                                        "id": "wamid.test",
                                        "type": "text",
                                        "text": {"body": "ok"},
                                    }
                                ]
                            }
                        }
                    ]
                }
            ],
        }
        response = client.post("/api/v1/webhooks/whatsapp", json=inbound)
        assert response.status_code == 200, response.text
        assert response.json()["verified"] == 1

        channels = client.get(
            "/api/v1/notification-channels",
            headers={"X-API-Key": api_key},
        )
        assert channels.status_code == 200
        wa = next(item for item in channels.json() if item["channel_type"] == "whatsapp")
        assert wa["is_verified"] is True
    finally:
        monkeypatch.delenv("SIGNUP_AUTO_VERIFY", raising=False)
        monkeypatch.setenv("APP_ENV", "development")
        get_settings.cache_clear()

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
    finally:
        get_settings.cache_clear()

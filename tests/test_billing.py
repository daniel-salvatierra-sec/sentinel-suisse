"""Billing / Stripe Premium checkout (Phase B)."""

import uuid
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.services.stripe_billing import (
    apply_checkout_completed,
    apply_subscription_deleted,
)


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def test_billing_config_public(client: TestClient) -> None:
    response = client.get("/api/v1/billing/config")
    assert response.status_code == 200
    body = response.json()
    assert "payments_enabled" in body
    assert "twint_enabled" in body


def test_billing_status_and_checkout_disabled(
    client: TestClient, admin_auth: tuple[str, str], monkeypatch
) -> None:
    monkeypatch.setenv("STRIPE_SECRET_KEY", "")
    monkeypatch.setenv("STRIPE_PRICE_ID", "")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    created = client.post(
        "/api/v1/users",
        json={"email": _email("bill"), "is_active": True, "locale": "fr"},
        auth=admin_auth,
    )
    assert created.status_code == 201, created.text
    headers = {"X-API-Key": created.json()["api_key"]}

    status = client.get("/api/v1/billing/status", headers=headers)
    assert status.status_code == 200
    assert status.json()["payments_enabled"] is False
    assert status.json()["is_premium"] is False

    checkout = client.post("/api/v1/billing/checkout", headers=headers)
    assert checkout.status_code == 503
    assert checkout.json()["detail"] == "payments_disabled"


def test_checkout_blocked_when_already_premium(
    client: TestClient, admin_auth: tuple[str, str], monkeypatch
) -> None:
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_PRICE_ID", "price_test")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    created = client.post(
        "/api/v1/users",
        json={
            "email": _email("prem-bill"),
            "is_active": True,
            "locale": "fr",
            "is_premium": True,
        },
        auth=admin_auth,
    )
    assert created.status_code == 201, created.text
    headers = {"X-API-Key": created.json()["api_key"]}

    checkout = client.post("/api/v1/billing/checkout", headers=headers)
    assert checkout.status_code == 400
    assert checkout.json()["detail"] == "already_premium"


def test_apply_checkout_and_subscription_lifecycle(
    client: TestClient, admin_auth: tuple[str, str]
) -> None:
    created = client.post(
        "/api/v1/users",
        json={"email": _email("stripe-life"), "is_active": True, "locale": "fr"},
        auth=admin_auth,
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]
    api_key = created.json()["api_key"]
    headers = {"X-API-Key": api_key}

    db = SessionLocal()
    try:
        user = apply_checkout_completed(
            db,
            {
                "metadata": {"user_id": str(user_id)},
                "customer": "cus_test_123",
                "subscription": "sub_test_456",
            },
        )
        assert user is not None
        assert user.is_premium is True
        assert user.stripe_customer_id == "cus_test_123"
        assert user.stripe_subscription_id == "sub_test_456"
    finally:
        db.close()

    me = client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["is_premium"] is True

    db = SessionLocal()
    try:
        revoked = apply_subscription_deleted(
            db,
            {"id": "sub_test_456", "metadata": {"user_id": str(user_id)}},
        )
        assert revoked is not None
        assert revoked.is_premium is False
    finally:
        db.close()

    me2 = client.get("/api/v1/users/me", headers=headers)
    assert me2.json()["is_premium"] is False


def test_stripe_webhook_rejects_bad_signature(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    response = client.post(
        "/api/v1/webhooks/stripe",
        content=b'{"id":"evt_1"}',
        headers={"Content-Type": "application/json", "Stripe-Signature": "bad"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid_signature"


def test_stripe_webhook_checkout_completed(
    client: TestClient, admin_auth: tuple[str, str], monkeypatch
) -> None:
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    created = client.post(
        "/api/v1/users",
        json={"email": _email("wh"), "is_active": True, "locale": "fr"},
        auth=admin_auth,
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]
    headers = {"X-API-Key": created.json()["api_key"]}

    fake_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {"user_id": str(user_id)},
                "customer": "cus_wh",
                "subscription": "sub_wh",
            }
        },
    }

    with patch(
        "sentinel_suisse.api.routes.stripe_webhooks.construct_event",
        return_value=fake_event,
    ):
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=b"{}",
            headers={"Content-Type": "application/json", "Stripe-Signature": "t=1"},
        )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ok"

    me = client.get("/api/v1/users/me", headers=headers)
    assert me.json()["is_premium"] is True


def test_refunds_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/legal/refunds")
    assert response.status_code == 200
    body = response.json()
    assert "Refund" in body["content"] or "refund" in body["content"].lower()
    assert body["version"]


def test_checkout_creates_stripe_session(
    client: TestClient, admin_auth: tuple[str, str], monkeypatch
) -> None:
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_PRICE_ID", "price_test")
    monkeypatch.setenv("STRIPE_ENABLE_TWINT", "true")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    created = client.post(
        "/api/v1/users",
        json={"email": _email("co"), "is_active": True, "locale": "fr"},
        auth=admin_auth,
    )
    assert created.status_code == 201, created.text
    headers = {"X-API-Key": created.json()["api_key"]}

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/c/pay/cs_test"

    with patch(
        "sentinel_suisse.services.stripe_billing.stripe.checkout.Session.create",
        return_value=mock_session,
    ) as create_mock:
        response = client.post("/api/v1/billing/checkout", headers=headers)

    assert response.status_code == 200, response.text
    assert response.json()["checkout_url"].startswith("https://checkout.stripe.com/")
    create_mock.assert_called_once()
    kwargs = create_mock.call_args.kwargs
    assert kwargs["mode"] == "subscription"
    assert kwargs["payment_method_types"] == ["card", "twint"]

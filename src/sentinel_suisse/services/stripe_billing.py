"""Stripe Checkout + webhook handlers for Premium subscriptions."""

from __future__ import annotations

import logging
from typing import Any

import stripe
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.models.user import User
from sentinel_suisse.security.pii import decrypt_pii

logger = logging.getLogger(__name__)


class BillingError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def _configure_stripe(settings: Settings) -> None:
    stripe.api_key = settings.stripe_secret_key


def create_checkout_session(db: Session, user: User, settings: Settings) -> str:
    """Create a Stripe Checkout Session; return the hosted URL."""
    if not settings.stripe_payments_enabled():
        raise BillingError("payments_disabled", "Stripe payments are not configured.")

    _configure_stripe(settings)
    base = settings.public_app_url.rstrip("/")
    email = decrypt_pii(user.email)

    params: dict[str, Any] = {
        "mode": "subscription",
        "line_items": [{"price": settings.stripe_price_id, "quantity": 1}],
        "success_url": f"{base}/?premium=success",
        "cancel_url": f"{base}/?premium=cancel",
        "client_reference_id": str(user.id),
        "customer_email": email,
        "metadata": {"user_id": str(user.id)},
        "subscription_data": {"metadata": {"user_id": str(user.id)}},
    }
    if user.stripe_customer_id:
        params["customer"] = user.stripe_customer_id
        params.pop("customer_email", None)

    if settings.stripe_enable_twint:
        # Card + TWINT (CH) when enabled in the Stripe Dashboard.
        params["payment_method_types"] = ["card", "twint"]
    else:
        params["automatic_payment_methods"] = {"enabled": True}

    session = stripe.checkout.Session.create(**params)
    url = session.url
    if not url:
        raise BillingError("checkout_failed", "Stripe did not return a checkout URL.")
    return str(url)


def apply_checkout_completed(db: Session, session_obj: dict[str, Any]) -> User | None:
    """Mark user premium from checkout.session.completed payload."""
    metadata = session_obj.get("metadata") or {}
    user_id_raw = metadata.get("user_id") or session_obj.get("client_reference_id")
    if not user_id_raw:
        logger.warning("stripe checkout missing user_id")
        return None
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        logger.warning("stripe checkout invalid user_id=%s", user_id_raw)
        return None

    user = db.get(User, user_id)
    if user is None:
        logger.warning("stripe checkout user not found id=%s", user_id)
        return None

    customer = session_obj.get("customer")
    subscription = session_obj.get("subscription")
    if isinstance(customer, str) and customer:
        user.stripe_customer_id = customer
    if isinstance(subscription, str) and subscription:
        user.stripe_subscription_id = subscription
    user.is_premium = True
    db.commit()
    db.refresh(user)
    logger.info("stripe premium activated user_id=%s", user.id)
    return user


def apply_subscription_deleted(db: Session, subscription_obj: dict[str, Any]) -> User | None:
    """Revoke premium when subscription ends."""
    sub_id = subscription_obj.get("id")
    metadata = subscription_obj.get("metadata") or {}
    user: User | None = None
    if metadata.get("user_id"):
        try:
            user = db.get(User, int(metadata["user_id"]))
        except (TypeError, ValueError):
            user = None
    if user is None and isinstance(sub_id, str):
        from sqlalchemy import select

        user = db.scalar(select(User).where(User.stripe_subscription_id == sub_id))

    if user is None:
        return None
    user.is_premium = False
    if isinstance(sub_id, str):
        user.stripe_subscription_id = None
    db.commit()
    db.refresh(user)
    logger.info("stripe premium revoked user_id=%s", user.id)
    return user


def construct_event(payload: bytes, sig_header: str | None, settings: Settings) -> stripe.Event:
    if not settings.stripe_webhook_secret:
        raise BillingError("webhook_unconfigured", "STRIPE_WEBHOOK_SECRET is not set.")
    try:
        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except ValueError as exc:
        raise BillingError("invalid_signature", "Invalid Stripe webhook signature.") from exc
    except Exception as exc:
        # stripe.SignatureVerificationError (v11+) or stripe.error.* (legacy)
        if "SignatureVerification" in type(exc).__name__:
            raise BillingError("invalid_signature", "Invalid Stripe webhook signature.") from exc
        raise

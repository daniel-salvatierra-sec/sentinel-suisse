"""Stripe Checkout + webhook handlers for Premium subscriptions."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import stripe
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.sponsor_ad import SponsorAd
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


def _resolve_promotion_code_id(code: str) -> str | None:
    """Look up an active Stripe Promotion Code id by its customer-facing code."""
    needle = code.strip()
    if not needle:
        return None
    try:
        found = stripe.PromotionCode.list(code=needle, active=True, limit=1)
    except Exception:
        logger.exception("stripe promotion code lookup failed code=%s", needle)
        return None
    data = getattr(found, "data", None) or []
    if not data:
        return None
    promo_id = getattr(data[0], "id", None)
    return str(promo_id) if promo_id else None


def create_checkout_session(
    db: Session,
    user: User,
    settings: Settings,
    *,
    promotion_code: str | None = None,
) -> str:
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
        # setup_future_usage is required for recurring TWINT subscriptions.
        params["payment_method_types"] = ["card", "twint"]
        params["payment_method_options"] = {
            "twint": {"setup_future_usage": "off_session"},
        }
    # else: omit payment_method_types entirely so Stripe uses whatever
    # payment methods are enabled in the Dashboard (e.g. card only while
    # TWINT is pending approval). Checkout Sessions don't accept the
    # PaymentIntent-only "automatic_payment_methods" parameter.

    # Prefer auto-applying a known promo (launch / shared link). Stripe forbids
    # combining discounts= with allow_promotion_codes=true on the same session.
    code = (promotion_code or settings.stripe_launch_promo_code or "").strip()
    applied = False
    if code:
        promo_id = _resolve_promotion_code_id(code)
        if promo_id:
            params["discounts"] = [{"promotion_code": promo_id}]
            params["metadata"]["promotion_code"] = code
            applied = True
        else:
            logger.warning("stripe promotion code not found code=%s", code)
    if not applied and settings.stripe_allow_promotion_codes:
        params["allow_promotion_codes"] = True

    session = stripe.checkout.Session.create(**params)
    url = session.url
    if not url:
        raise BillingError("checkout_failed", "Stripe did not return a checkout URL.")
    return str(url)


def create_billing_portal_session(user: User, settings: Settings) -> str:
    """Create a Stripe Customer Portal session so the user can manage/cancel Premium."""
    if not settings.stripe_payments_enabled():
        raise BillingError("payments_disabled", "Stripe payments are not configured.")
    if not user.stripe_customer_id:
        raise BillingError(
            "no_stripe_customer",
            "No Stripe customer linked to this account.",
        )

    _configure_stripe(settings)
    base = settings.public_app_url.rstrip("/")
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{base}/?tab=account&premium=portal",
    )
    url = session.url
    if not url:
        raise BillingError("portal_failed", "Stripe did not return a portal URL.")
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

    payment_status = session_obj.get("payment_status")
    subscription = session_obj.get("subscription")
    # Card checkouts are usually "paid". Async methods (e.g. TWINT) may be
    # "unpaid" briefly but still create a subscription — activate only if
    # Stripe already attached one; otherwise wait for a later event.
    if payment_status == "unpaid" and not subscription:
        logger.warning(
            "stripe checkout unpaid without subscription user_id=%s",
            user_id,
        )
        return None

    customer = session_obj.get("customer")
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


def create_feature_checkout_session(
    *,
    listing: Listing,
    user: User,
    settings: Settings,
) -> str:
    """One-time payment Checkout to boost a direct listing."""
    if not settings.stripe_feature_payments_enabled():
        raise BillingError("feature_payments_disabled", "Listing boost is not configured.")
    if listing.owner_user_id != user.id:
        raise BillingError("listing_forbidden", "You can only boost your own listings.")

    _configure_stripe(settings)
    base = settings.public_app_url.rstrip("/")
    email = decrypt_pii(user.email)
    params: dict[str, Any] = {
        "mode": "payment",
        "line_items": [{"price": settings.stripe_feature_price_id, "quantity": 1}],
        "success_url": f"{base}/?boost=success",
        "cancel_url": f"{base}/?boost=cancel",
        "client_reference_id": str(user.id),
        "customer_email": email,
        "metadata": {
            "user_id": str(user.id),
            "listing_id": str(listing.id),
            "purpose": "feature_listing",
        },
    }
    if user.stripe_customer_id:
        params["customer"] = user.stripe_customer_id
        params.pop("customer_email", None)

    session = stripe.checkout.Session.create(**params)
    url = session.url
    if not url:
        raise BillingError("checkout_failed", "Stripe did not return a checkout URL.")
    return str(url)


def apply_feature_checkout_completed(
    db: Session,
    session_obj: dict[str, Any],
    *,
    feature_days: int,
) -> Listing | None:
    """Mark listing featured after a successful one-time Checkout."""
    metadata = session_obj.get("metadata") or {}
    if metadata.get("purpose") != "feature_listing":
        return None

    payment_status = session_obj.get("payment_status")
    if payment_status not in {None, "paid", "no_payment_required"}:
        logger.warning(
            "stripe feature checkout not paid status=%s listing_id=%s",
            payment_status,
            metadata.get("listing_id"),
        )
        return None

    listing_id_raw = metadata.get("listing_id")
    if not listing_id_raw:
        logger.warning("stripe feature checkout missing listing_id")
        return None
    try:
        listing_id = int(listing_id_raw)
    except (TypeError, ValueError):
        logger.warning("stripe feature checkout invalid listing_id=%s", listing_id_raw)
        return None

    listing = db.get(Listing, listing_id)
    if listing is None:
        logger.warning("stripe feature checkout listing not found id=%s", listing_id)
        return None

    owner_raw = metadata.get("user_id")
    if owner_raw is not None:
        try:
            if listing.owner_user_id != int(owner_raw):
                logger.warning(
                    "stripe feature checkout owner mismatch listing_id=%s",
                    listing_id,
                )
                return None
        except (TypeError, ValueError):
            return None

    days = max(1, feature_days)
    now = datetime.now(UTC)
    current_until = listing.featured_until
    if current_until is not None and current_until.tzinfo is None:
        current_until = current_until.replace(tzinfo=UTC)
    base = current_until if current_until and current_until > now else now
    listing.is_featured = True
    listing.featured_until = base + timedelta(days=days)
    db.commit()
    db.refresh(listing)
    logger.info(
        "stripe listing featured id=%s until=%s",
        listing.id,
        listing.featured_until,
    )
    return listing


def create_sponsor_checkout_session(
    db: Session,
    *,
    sponsor: SponsorAd,
    user: User,
    settings: Settings,
) -> str:
    """One-time payment Checkout to publish a sponsor banner."""
    if not settings.stripe_sponsor_payments_enabled():
        raise BillingError("sponsor_payments_disabled", "Sponsor ads checkout is not configured.")
    if sponsor.owner_user_id != user.id:
        raise BillingError("sponsor_forbidden", "You can only pay for your own sponsor ads.")
    if sponsor.is_active:
        raise BillingError("sponsor_already_active", "This sponsor ad is already live.")

    _configure_stripe(settings)
    base = settings.public_app_url.rstrip("/")
    email = decrypt_pii(user.email)
    params: dict[str, Any] = {
        "mode": "payment",
        "line_items": [{"price": settings.stripe_sponsor_price_id, "quantity": 1}],
        "success_url": f"{base}/?sponsor=success",
        "cancel_url": f"{base}/?sponsor=cancel",
        "client_reference_id": str(user.id),
        "customer_email": email,
        "metadata": {
            "user_id": str(user.id),
            "sponsor_id": str(sponsor.id),
            "purpose": "sponsor_ad",
        },
    }
    if user.stripe_customer_id:
        params["customer"] = user.stripe_customer_id
        params.pop("customer_email", None)

    session = stripe.checkout.Session.create(**params)
    url = session.url
    if not url:
        raise BillingError("checkout_failed", "Stripe did not return a checkout URL.")

    sponsor.stripe_checkout_id = str(session.id)
    db.commit()
    db.refresh(sponsor)
    return str(url)


def apply_sponsor_checkout_completed(
    db: Session,
    session_obj: dict[str, Any],
    *,
    sponsor_days: int,
) -> SponsorAd | None:
    """Activate a sponsor banner after successful one-time Checkout."""
    metadata = session_obj.get("metadata") or {}
    if metadata.get("purpose") != "sponsor_ad":
        return None

    payment_status = session_obj.get("payment_status")
    if payment_status not in {None, "paid", "no_payment_required"}:
        logger.warning(
            "stripe sponsor checkout not paid status=%s sponsor_id=%s",
            payment_status,
            metadata.get("sponsor_id"),
        )
        return None

    sponsor_id_raw = metadata.get("sponsor_id")
    if not sponsor_id_raw:
        logger.warning("stripe sponsor checkout missing sponsor_id")
        return None
    try:
        sponsor_id = int(sponsor_id_raw)
    except (TypeError, ValueError):
        logger.warning("stripe sponsor checkout invalid sponsor_id=%s", sponsor_id_raw)
        return None

    sponsor = db.get(SponsorAd, sponsor_id)
    if sponsor is None:
        logger.warning("stripe sponsor checkout sponsor not found id=%s", sponsor_id)
        return None

    checkout_id = session_obj.get("id")
    if isinstance(checkout_id, str) and checkout_id:
        if sponsor.stripe_checkout_id and sponsor.stripe_checkout_id != checkout_id:
            logger.warning(
                "stripe sponsor checkout id mismatch sponsor_id=%s",
                sponsor_id,
            )
            return None
        sponsor.stripe_checkout_id = checkout_id

    owner_raw = metadata.get("user_id")
    if owner_raw is not None and sponsor.owner_user_id is not None:
        try:
            if sponsor.owner_user_id != int(owner_raw):
                logger.warning(
                    "stripe sponsor checkout owner mismatch sponsor_id=%s",
                    sponsor_id,
                )
                return None
        except (TypeError, ValueError):
            return None

    if sponsor.is_active and sponsor.starts_at is not None:
        return sponsor

    days = max(1, sponsor_days)
    now = datetime.now(UTC)
    total = session_obj.get("amount_total")
    if total is not None:
        from decimal import Decimal

        sponsor.monthly_chf = (Decimal(str(total)) / Decimal("100")).quantize(Decimal("0.01"))

    sponsor.is_active = True
    sponsor.starts_at = now
    sponsor.ends_at = now + timedelta(days=days)
    db.commit()
    db.refresh(sponsor)
    logger.info(
        "stripe sponsor activated id=%s until=%s",
        sponsor.id,
        sponsor.ends_at,
    )
    return sponsor


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

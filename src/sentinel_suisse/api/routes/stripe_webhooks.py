"""Stripe webhook — Checkout + subscription lifecycle."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.services.stripe_billing import (
    BillingError,
    apply_checkout_completed,
    apply_feature_checkout_completed,
    apply_sponsor_checkout_completed,
    apply_subscription_deleted,
    construct_event,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/stripe", tags=["webhooks"])


def _settings() -> Settings:
    return get_settings()


@router.post("")
@limiter.limit("120/minute")
async def stripe_webhook(
    request: Request,
    settings: Settings = Depends(_settings),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature")
    try:
        event = construct_event(payload, sig, settings)
    except BillingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.code,
        ) from exc

    event_type = event["type"]
    data_object = event["data"]["object"]
    logger.info("stripe_webhook type=%s", event_type)

    if event_type == "checkout.session.completed":
        session_obj = dict(data_object)
        metadata = session_obj.get("metadata") or {}
        purpose = metadata.get("purpose")
        if purpose == "feature_listing":
            apply_feature_checkout_completed(
                db,
                session_obj,
                feature_days=settings.stripe_feature_days,
            )
        elif purpose == "sponsor_ad":
            apply_sponsor_checkout_completed(
                db,
                session_obj,
                sponsor_days=settings.stripe_sponsor_days,
            )
        else:
            apply_checkout_completed(db, session_obj)
    elif event_type in {"customer.subscription.deleted", "customer.subscription.paused"}:
        apply_subscription_deleted(db, dict(data_object))

    return {"status": "ok"}

"""Billing / Premium checkout routes (authenticated)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import get_current_user
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.user import User
from sentinel_suisse.services.stripe_billing import BillingError, create_checkout_session

router = APIRouter(prefix="/billing", tags=["billing"])


class BillingConfig(BaseModel):
    payments_enabled: bool
    twint_enabled: bool


class BillingStatus(BaseModel):
    payments_enabled: bool
    is_premium: bool
    twint_enabled: bool


class CheckoutResponse(BaseModel):
    checkout_url: str


@router.get("/config", response_model=BillingConfig)
@limiter.limit(lambda: get_settings().rate_limit)
def billing_config(request: Request) -> BillingConfig:
    """Public: whether Stripe Checkout is configured (no auth)."""
    settings = get_settings()
    return BillingConfig(
        payments_enabled=settings.stripe_payments_enabled(),
        twint_enabled=settings.stripe_enable_twint,
    )


@router.get("/status", response_model=BillingStatus)
@limiter.limit(lambda: get_settings().rate_limit)
def billing_status(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> BillingStatus:
    settings = get_settings()
    return BillingStatus(
        payments_enabled=settings.stripe_payments_enabled(),
        is_premium=current_user.is_premium,
        twint_enabled=settings.stripe_enable_twint,
    )


@router.post("/checkout", response_model=CheckoutResponse)
@limiter.limit("10/minute")
def start_checkout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutResponse:
    if current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already_premium",
        )
    settings = get_settings()
    try:
        url = create_checkout_session(db, current_user, settings)
    except BillingError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            if exc.code == "payments_disabled"
            else status.HTTP_400_BAD_REQUEST,
            detail=exc.code,
        ) from exc
    return CheckoutResponse(checkout_url=url)

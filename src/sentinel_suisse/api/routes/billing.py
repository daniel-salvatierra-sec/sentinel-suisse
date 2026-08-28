"""Billing / Premium checkout routes (authenticated)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import get_current_user
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.sponsor_ad import SponsorCheckoutRequest
from sentinel_suisse.services.sponsor_ads import create_pending_sponsor
from sentinel_suisse.services.stripe_billing import (
    BillingError,
    create_billing_portal_session,
    create_checkout_session,
    create_feature_checkout_session,
    create_sponsor_checkout_session,
)

router = APIRouter(prefix="/billing", tags=["billing"])


class BillingConfig(BaseModel):
    payments_enabled: bool
    twint_enabled: bool
    launch_promo_code: str | None = None
    launch_promo_percent: int | None = None
    launch_promo_months: int | None = None
    feature_boost_enabled: bool = False
    feature_boost_days: int = 7
    sponsor_ads_enabled: bool = False
    sponsor_ad_days: int = 30


class BillingStatus(BaseModel):
    payments_enabled: bool
    is_premium: bool
    twint_enabled: bool
    launch_promo_code: str | None = None
    launch_promo_percent: int | None = None
    launch_promo_months: int | None = None
    feature_boost_enabled: bool = False
    feature_boost_days: int = 7
    sponsor_ads_enabled: bool = False
    sponsor_ad_days: int = 30


class CheckoutRequest(BaseModel):
    promotion_code: str | None = None


class FeatureCheckoutRequest(BaseModel):
    listing_id: int


class CheckoutResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str


def _launch_promo_fields(settings) -> dict[str, str | int | None]:
    code = (settings.stripe_launch_promo_code or "").strip() or None
    if not code:
        return {
            "launch_promo_code": None,
            "launch_promo_percent": None,
            "launch_promo_months": None,
        }
    return {
        "launch_promo_code": code,
        "launch_promo_percent": settings.stripe_launch_promo_percent,
        "launch_promo_months": settings.stripe_launch_promo_months,
    }


def _feature_fields(settings) -> dict[str, bool | int]:
    return {
        "feature_boost_enabled": settings.stripe_feature_payments_enabled(),
        "feature_boost_days": settings.stripe_feature_days,
    }


def _sponsor_fields(settings) -> dict[str, bool | int]:
    return {
        "sponsor_ads_enabled": settings.stripe_sponsor_payments_enabled(),
        "sponsor_ad_days": settings.stripe_sponsor_days,
    }


@router.get("/config", response_model=BillingConfig)
@limiter.limit(lambda: get_settings().rate_limit)
def billing_config(request: Request) -> BillingConfig:
    """Public: whether Stripe Checkout is configured (no auth)."""
    settings = get_settings()
    return BillingConfig(
        payments_enabled=settings.stripe_payments_enabled(),
        twint_enabled=settings.stripe_enable_twint,
        **_launch_promo_fields(settings),
        **_feature_fields(settings),
        **_sponsor_fields(settings),
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
        **_launch_promo_fields(settings),
        **_feature_fields(settings),
        **_sponsor_fields(settings),
    )


@router.post("/checkout", response_model=CheckoutResponse)
@limiter.limit("10/minute")
def start_checkout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    payload: CheckoutRequest = CheckoutRequest(),
) -> CheckoutResponse:
    if current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already_premium",
        )
    settings = get_settings()
    promo = payload.promotion_code
    try:
        url = create_checkout_session(
            db,
            current_user,
            settings,
            promotion_code=promo,
        )
    except BillingError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            if exc.code == "payments_disabled"
            else status.HTTP_400_BAD_REQUEST,
            detail=exc.code,
        ) from exc
    return CheckoutResponse(checkout_url=url)


@router.post("/feature-checkout", response_model=CheckoutResponse)
@limiter.limit("10/minute")
def start_feature_checkout(
    request: Request,
    payload: FeatureCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutResponse:
    listing = db.get(Listing, payload.listing_id)
    if listing is None or listing.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="listing_not_found",
        )
    settings = get_settings()
    try:
        url = create_feature_checkout_session(
            listing=listing,
            user=current_user,
            settings=settings,
        )
    except BillingError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            if exc.code == "feature_payments_disabled"
            else status.HTTP_400_BAD_REQUEST,
            detail=exc.code,
        ) from exc
    return CheckoutResponse(checkout_url=url)


@router.post("/sponsor-checkout", response_model=CheckoutResponse)
@limiter.limit("10/minute")
def start_sponsor_checkout(
    request: Request,
    payload: SponsorCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutResponse:
    settings = get_settings()
    sponsor = create_pending_sponsor(db, current_user, payload)
    try:
        url = create_sponsor_checkout_session(
            db,
            sponsor=sponsor,
            user=current_user,
            settings=settings,
        )
    except BillingError as exc:
        db.delete(sponsor)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            if exc.code == "sponsor_payments_disabled"
            else status.HTTP_400_BAD_REQUEST,
            detail=exc.code,
        ) from exc
    return CheckoutResponse(checkout_url=url)


@router.post("/portal", response_model=PortalResponse)
@limiter.limit("10/minute")
def start_portal(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> PortalResponse:
    """Open Stripe Customer Portal (cancel / update payment method)."""
    settings = get_settings()
    try:
        url = create_billing_portal_session(current_user, settings)
    except BillingError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            if exc.code == "payments_disabled"
            else status.HTTP_400_BAD_REQUEST,
            detail=exc.code,
        ) from exc
    return PortalResponse(portal_url=url)

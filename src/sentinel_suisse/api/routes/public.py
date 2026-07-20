"""Public read-only endpoints for the web UI (development / demo)."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType, PropertyType
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.models.provider import Provider
from sentinel_suisse.schemas.listing import ListingRead
from sentinel_suisse.schemas.provider import ProviderRead
from sentinel_suisse.schemas.public_signup import (
    ChannelVerificationResponse,
    EmailVerificationResponse,
    PublicAlertSignup,
    PublicAlertSignupResponse,
)
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.email_verification import (
    send_channel_verification_email,
    send_channel_verification_whatsapp,
    verify_channel_by_token,
    verify_email_channel,
)
from sentinel_suisse.services.entitlements import EntitlementError
from sentinel_suisse.services.public_signup import subscribe_public_alert
from sentinel_suisse.services.search import search_listings

router = APIRouter(prefix="/public", tags=["public"])


def _require_public_search() -> None:
    settings = get_settings()
    if not settings.public_search_is_enabled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public search is not available",
        )


def _require_public_signup() -> None:
    settings = get_settings()
    if not settings.public_signup_is_enabled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public signup is not available",
        )


@router.get("/providers", response_model=list[ProviderRead])
@limiter.limit(lambda: get_settings().rate_limit)
def public_providers(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_require_public_search),
) -> list[Provider]:
    """Active providers for public filter chips (same gate as search)."""
    return list(
        db.scalars(
            select(Provider).where(Provider.is_active.is_(True)).order_by(Provider.name)
        ).all()
    )


@router.get("/search", response_model=list[ListingRead])
@limiter.limit(lambda: get_settings().rate_limit)
def public_search(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_require_public_search),
    listing_type: ListingType | None = Query(default=None),
    location: str | None = Query(default=None, min_length=1, max_length=200),
    country: CountryCode | None = Query(default=None),
    price_min: float | None = Query(default=None, ge=0),
    price_max: float | None = Query(default=None, ge=0),
    rooms_min: float | None = Query(default=None, ge=0, le=20),
    property_type: PropertyType | None = Query(default=None),
    has_parking: bool | None = Query(default=None),
    job_category: str | None = Query(default=None, min_length=1, max_length=80),
    employment_type: EmploymentType | None = Query(default=None),
    workload_min: int | None = Query(default=None, ge=0, le=100),
    workload_max: int | None = Query(default=None, ge=0, le=100),
    provider_id: int | None = Query(default=None, gt=0),
    provider_ids: list[int] | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[ListingRead]:
    """Unauthenticated listing search for the public UI (opt-in in production)."""
    try:
        filters = SearchQuery(
            listing_type=listing_type,
            location=location,
            country=country,
            price_min=price_min,
            price_max=price_max,
            rooms_min=rooms_min,
            property_type=property_type,
            has_parking=has_parking,
            job_category=job_category,
            employment_type=employment_type,
            workload_min=workload_min,
            workload_max=workload_max,
            provider_id=provider_id,
            provider_ids=provider_ids,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="invalid search filters",
        ) from exc
    return search_listings(db, filters, limit=limit, offset=offset)


@router.post(
    "/signup", response_model=PublicAlertSignupResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def public_signup(
    request: Request,
    payload: PublicAlertSignup,
    db: Session = Depends(get_db),
    _: None = Depends(_require_public_signup),
) -> PublicAlertSignupResponse:
    """Create user, notification channels, and saved search from the public UI."""
    settings = get_settings()
    auto_verify = settings.signup_channels_auto_verify()
    try:
        result = subscribe_public_alert(
            db,
            payload,
            auto_verify_channels=auto_verify,
        )
    except EntitlementError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exc.code,
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from exc

    verification_email_sent = False
    whatsapp_verification_sent = False
    if not auto_verify:
        send_channel_verification_email(
            settings,
            email=str(payload.email).lower(),
            locale=payload.locale,
            channel_id=result.email_channel_id,
            user_id=result.user.id,
        )
        verification_email_sent = True
        if payload.phone and result.whatsapp_channel_id is not None:
            send_channel_verification_whatsapp(
                settings,
                phone=payload.phone,
                locale=payload.locale,
                channel_id=result.whatsapp_channel_id,
                user_id=result.user.id,
            )
            whatsapp_verification_sent = True

    verification_pending = not result.email_verified or (
        payload.phone is not None and not result.whatsapp_verified
    )
    return PublicAlertSignupResponse(
        api_key=result.api_key,
        user_id=result.user.id,
        saved_search_id=result.saved_search.id,
        email_verified=result.email_verified,
        whatsapp_verified=result.whatsapp_verified,
        verification_pending=verification_pending,
        verification_email_sent=verification_email_sent,
        whatsapp_verification_sent=whatsapp_verification_sent,
    )


def _verify_channel_response(channel: NotificationChannel) -> ChannelVerificationResponse:
    label = channel.channel_type.value
    return ChannelVerificationResponse(
        verified=True,
        channel_type=label,
        message=f"{label} channel verified",
    )


@router.get("/verify-channel", response_model=ChannelVerificationResponse)
@limiter.limit("20/minute")
def public_verify_channel(
    request: Request,
    token: str = Query(min_length=10),
    db: Session = Depends(get_db),
) -> ChannelVerificationResponse:
    """Confirm any notification channel via signed link (all environments)."""
    try:
        channel = verify_channel_by_token(db, token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _verify_channel_response(channel)


@router.get("/verify-email", response_model=EmailVerificationResponse)
@limiter.limit("20/minute")
def public_verify_email(
    request: Request,
    token: str = Query(min_length=10),
    db: Session = Depends(get_db),
) -> EmailVerificationResponse:
    """Confirm email notification channel via signed link (all environments)."""
    try:
        channel = verify_email_channel(db, token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    response = _verify_channel_response(channel)
    return EmailVerificationResponse(**response.model_dump())

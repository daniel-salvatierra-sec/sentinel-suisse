"""Private operator dashboard API (HTTP Basic admin)."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import verify_admin
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.sponsor_ad import SponsorAd
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.admin_dashboard import (
    AdminInsights,
    AdminListingCreate,
    AdminListingRow,
    AdminListingUpdate,
    DashboardOverview,
    ListingVisibilityUpdate,
    UserFreeAlertsUpdate,
    UserPremiumUpdate,
)
from sentinel_suisse.schemas.erasure import UserErasureReport
from sentinel_suisse.schemas.sponsor_ad import SponsorAdAdminRow, SponsorAdCreate, SponsorAdUpdate
from sentinel_suisse.schemas.user import UserRead
from sentinel_suisse.services.admin_dashboard import (
    dashboard_overview,
    list_admin_listings,
    listing_to_row,
    readable_user_rows,
    set_listing_hidden,
    set_user_free_alerts,
    user_row,
)
from sentinel_suisse.services.admin_insights import admin_insights
from sentinel_suisse.services.direct_listings import create_admin_listing, update_admin_listing
from sentinel_suisse.services.erasure import erase_user
from sentinel_suisse.services.sponsor_ads import (
    create_sponsor,
    delete_sponsor,
    list_admin_sponsors,
    update_sponsor,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=DashboardOverview)
@limiter.limit(lambda: get_settings().rate_limit)
def get_overview(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> DashboardOverview:
    return dashboard_overview(db)


@router.get("/insights", response_model=AdminInsights)
@limiter.limit(lambda: get_settings().rate_limit)
def get_insights(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> AdminInsights:
    return admin_insights(db, get_settings())


@router.get("/sponsors", response_model=list[SponsorAdAdminRow])
@limiter.limit(lambda: get_settings().rate_limit)
def get_sponsors(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[SponsorAdAdminRow]:
    return list_admin_sponsors(db, limit=limit)


@router.post("/sponsors", response_model=SponsorAdAdminRow, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def post_sponsor(
    request: Request,
    payload: SponsorAdCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> SponsorAdAdminRow:
    return create_sponsor(db, payload)


@router.patch("/sponsors/{sponsor_id}", response_model=SponsorAdAdminRow)
@limiter.limit(lambda: get_settings().rate_limit)
def patch_sponsor(
    request: Request,
    sponsor_id: int,
    payload: SponsorAdUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> SponsorAdAdminRow:
    row = db.get(SponsorAd, sponsor_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found")
    try:
        return update_sponsor(db, row, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.delete("/sponsors/{sponsor_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(lambda: get_settings().rate_limit)
def remove_sponsor(
    request: Request,
    sponsor_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> None:
    row = db.get(SponsorAd, sponsor_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found")
    delete_sponsor(db, row)


@router.get("/listings", response_model=list[AdminListingRow])
@limiter.limit(lambda: get_settings().rate_limit)
def get_listings(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
    q: str | None = Query(default=None, min_length=1, max_length=200),
    listing_type: ListingType | None = Query(default=None),
    hidden: bool | None = Query(default=None),
    owner_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AdminListingRow]:
    return list_admin_listings(
        db,
        q=q,
        listing_type=listing_type,
        hidden=hidden,
        owner_only=owner_only,
        limit=limit,
    )


@router.post("/listings", response_model=AdminListingRow, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def post_listing(
    request: Request,
    payload: AdminListingCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> AdminListingRow:
    if payload.owner_user_id is not None and db.get(User, payload.owner_user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    listing = create_admin_listing(db, payload, get_settings())
    slug = listing.provider.slug if listing.provider is not None else "direct"
    return listing_to_row(listing, slug)


@router.patch("/listings/{listing_id}", response_model=AdminListingRow)
@limiter.limit(lambda: get_settings().rate_limit)
def patch_listing(
    request: Request,
    listing_id: int,
    payload: AdminListingUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> AdminListingRow:
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    listing = update_admin_listing(db, listing, payload)
    slug = listing.provider.slug if listing.provider is not None else ""
    return listing_to_row(listing, slug)


@router.patch("/listings/{listing_id}/visibility", response_model=AdminListingRow)
@limiter.limit(lambda: get_settings().rate_limit)
def patch_listing_visibility(
    request: Request,
    listing_id: int,
    payload: ListingVisibilityUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> AdminListingRow:
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    listing = set_listing_hidden(db, listing, payload.is_hidden)
    slug = listing.provider.slug if listing.provider is not None else ""
    return listing_to_row(listing, slug)


@router.get("/users", response_model=list[UserRead])
@limiter.limit(lambda: get_settings().rate_limit)
def get_recent_users(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[UserRead]:
    return readable_user_rows(db, limit=limit)


@router.patch("/users/{user_id}/premium", response_model=UserRead)
@limiter.limit(lambda: get_settings().rate_limit)
def patch_user_premium(
    request: Request,
    user_id: int,
    payload: UserPremiumUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> UserRead:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_premium = payload.is_premium
    db.commit()
    db.refresh(user)
    return user_row(db, user)


@router.patch("/users/{user_id}/free-alerts", response_model=UserRead)
@limiter.limit(lambda: get_settings().rate_limit)
def patch_user_free_alerts(
    request: Request,
    user_id: int,
    payload: UserFreeAlertsUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> UserRead:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = set_user_free_alerts(
        db,
        user,
        free_alerts_grandfathered=payload.free_alerts_grandfathered,
    )
    return user_row(db, user)


@router.delete("/users/{user_id}", response_model=UserErasureReport)
@limiter.limit(lambda: get_settings().rate_limit)
def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> UserErasureReport:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = erase_user(db, user)
    return UserErasureReport(
        user_id=result.user_id,
        notification_channels_removed=result.notification_channels_removed,
        saved_searches_removed=result.saved_searches_removed,
        alert_logs_removed=result.alert_logs_removed,
        listings_removed=result.listings_removed,
    )

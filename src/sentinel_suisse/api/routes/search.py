"""Listing search routes."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import verify_admin_or_user
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.schemas.listing import ListingRead
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.search import search_listings

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[ListingRead])
@limiter.limit(lambda: get_settings().rate_limit)
def search(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_or_user),
    listing_type: ListingType | None = Query(default=None),
    location: str | None = Query(default=None, min_length=1, max_length=200),
    price_min: float | None = Query(default=None, ge=0),
    price_max: float | None = Query(default=None, ge=0),
    provider_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[ListingRead]:
    filters = SearchQuery(
        listing_type=listing_type,
        location=location,
        price_min=price_min,
        price_max=price_max,
        provider_id=provider_id,
    )
    return search_listings(db, filters, limit=limit, offset=offset)

"""Public read-only endpoints for the web UI (development / demo)."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.schemas.listing import ListingRead
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.search import search_listings

router = APIRouter(prefix="/public", tags=["public"])


def _require_public_preview() -> None:
    settings = get_settings()
    if settings.app_env != "development":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public preview is not available",
        )


@router.get("/search", response_model=list[ListingRead])
@limiter.limit(lambda: get_settings().rate_limit)
def public_search(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_require_public_preview),
    listing_type: ListingType | None = Query(default=None),
    location: str | None = Query(default=None, min_length=1, max_length=200),
    price_min: float | None = Query(default=None, ge=0),
    price_max: float | None = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[ListingRead]:
    """Unauthenticated search for localhost UI demo only."""
    filters = SearchQuery(
        listing_type=listing_type,
        location=location,
        price_min=price_min,
        price_max=price_max,
    )
    return search_listings(db, filters, limit=limit, offset=offset)

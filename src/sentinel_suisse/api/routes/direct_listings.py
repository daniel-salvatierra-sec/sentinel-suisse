"""User-posted housing listings (X-API-Key)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import get_current_user
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.direct_listing import DirectListingCreate
from sentinel_suisse.schemas.listing import ListingRead
from sentinel_suisse.services.direct_listings import DirectListingLimitError, create_direct_listing

router = APIRouter(prefix="/me/listings", tags=["direct-listings"])


@router.get("", response_model=list[ListingRead])
@limiter.limit(lambda: get_settings().rate_limit)
def list_my_listings(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Listing]:
    stmt = (
        select(Listing).where(Listing.owner_user_id == current_user.id).order_by(Listing.id.desc())
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=ListingRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def post_my_listing(
    request: Request,
    payload: DirectListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Listing:
    try:
        return create_direct_listing(db, current_user, payload, get_settings())
    except DirectListingLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(lambda: get_settings().rate_limit)
def delete_my_listing(
    request: Request,
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    listing = db.get(Listing, listing_id)
    if listing is None or listing.owner_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    db.delete(listing)
    db.commit()

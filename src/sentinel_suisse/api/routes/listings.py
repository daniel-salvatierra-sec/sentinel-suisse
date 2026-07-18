"""Listing CRUD routes (admin only)."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import verify_admin
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.provider import Provider
from sentinel_suisse.schemas.listing import ListingCreate, ListingRead, ListingUpdate

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=list[ListingRead])
@limiter.limit(lambda: get_settings().rate_limit)
def list_listings(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
    provider_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Listing]:
    stmt = select(Listing).order_by(Listing.id).limit(limit).offset(offset)
    if provider_id is not None:
        stmt = stmt.where(Listing.provider_id == provider_id)
    return list(db.scalars(stmt).all())


@router.get("/{listing_id}", response_model=ListingRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_listing(
    request: Request,
    listing_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> Listing:
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return listing


@router.post("", response_model=ListingRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def create_listing(
    request: Request,
    payload: ListingCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> Listing:
    provider = db.get(Provider, payload.provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    listing = Listing(
        provider_id=payload.provider_id,
        external_id=payload.external_id,
        listing_type=payload.listing_type,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        price=payload.price,
        rooms=payload.rooms,
        property_type=payload.property_type,
        has_parking=payload.has_parking,
        job_category=payload.job_category,
        employment_type=payload.employment_type,
        workload_min=payload.workload_min,
        workload_max=payload.workload_max,
        source_url=str(payload.source_url),
        content_hash=payload.content_hash,
        fetched_at=payload.fetched_at,
    )
    db.add(listing)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Listing with this provider and external_id already exists",
        ) from exc
    db.refresh(listing)
    return listing


@router.patch("/{listing_id}", response_model=ListingRead)
@limiter.limit(lambda: get_settings().rate_limit)
def update_listing(
    request: Request,
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> Listing:
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    updates = payload.model_dump(exclude_unset=True)
    if "source_url" in updates and updates["source_url"] is not None:
        updates["source_url"] = str(updates["source_url"])

    for field, value in updates.items():
        setattr(listing, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Listing conflicts with existing external_id for provider",
        ) from exc
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(lambda: get_settings().rate_limit)
def delete_listing(
    request: Request,
    listing_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> None:
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    db.delete(listing)
    db.commit()

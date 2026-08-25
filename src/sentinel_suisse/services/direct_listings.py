"""User-posted housing and job ads (no paid feed). Apply goes to the owner's URL."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.hashing import compute_content_hash, utc_now
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.provider import Provider
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.admin_dashboard import AdminListingCreate, AdminListingUpdate
from sentinel_suisse.schemas.direct_listing import DirectListingCreate

DIRECT_SLUG = "direct"


class DirectListingLimitError(RuntimeError):
    """User has reached the free cap of landlord-posted ads."""


def get_or_create_direct_provider(db: Session, settings: Settings) -> Provider:
    provider = db.scalar(select(Provider).where(Provider.slug == DIRECT_SLUG))
    if provider is not None:
        return provider
    provider = Provider(
        name="Direct",
        slug=DIRECT_SLUG,
        base_url=settings.public_app_url.rstrip("/") or "https://linkswiss.ch",
        is_active=True,
    )
    db.add(provider)
    db.flush()
    return provider


def count_direct_listings(db: Session, user: User) -> int:
    return int(
        db.scalar(select(func.count()).select_from(Listing).where(Listing.owner_user_id == user.id))
        or 0
    )


def create_direct_listing(
    db: Session,
    user: User,
    payload: DirectListingCreate,
    settings: Settings,
) -> Listing:
    if count_direct_listings(db, user) >= settings.direct_max_listings:
        msg = f"Maximum {settings.direct_max_listings} listings per account"
        raise DirectListingLimitError(msg)

    provider = get_or_create_direct_provider(db, settings)
    external_id = f"direct-{user.id}-{uuid.uuid4().hex[:12]}"
    raw = RawListing(
        external_id=external_id,
        listing_type=payload.listing_type,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        country=payload.country,
        price=Decimal(str(payload.price)) if payload.price is not None else None,
        rooms=payload.rooms,
        property_type=payload.property_type,
        has_parking=payload.has_parking,
        job_category=payload.job_category,
        employment_type=payload.employment_type,
        workload_min=payload.workload_min,
        workload_max=payload.workload_max,
        source_url=str(payload.contact_url),
        raw_payload={"source": "direct", "user_id": user.id},
    )
    listing = Listing(
        provider_id=provider.id,
        owner_user_id=user.id,
        external_id=raw.external_id,
        listing_type=raw.listing_type,
        title=raw.title,
        description=raw.description,
        location=raw.location,
        country=raw.country,
        price=raw.price,
        rooms=raw.rooms,
        property_type=raw.property_type,
        has_parking=raw.has_parking,
        job_category=raw.job_category,
        employment_type=raw.employment_type,
        workload_min=raw.workload_min,
        workload_max=raw.workload_max,
        source_url=str(raw.source_url),
        content_hash=compute_content_hash(raw),
        raw_payload=raw.raw_payload,
        fetched_at=utc_now(),
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def _listing_from_raw(
    db: Session,
    *,
    provider: Provider,
    raw: RawListing,
    owner_user_id: int | None,
    is_hidden: bool,
    raw_payload: dict,
) -> Listing:
    listing = Listing(
        provider_id=provider.id,
        owner_user_id=owner_user_id,
        external_id=raw.external_id,
        listing_type=raw.listing_type,
        title=raw.title,
        description=raw.description,
        location=raw.location,
        country=raw.country,
        price=raw.price,
        rooms=raw.rooms,
        property_type=raw.property_type,
        has_parking=raw.has_parking,
        job_category=raw.job_category,
        employment_type=raw.employment_type,
        workload_min=raw.workload_min,
        workload_max=raw.workload_max,
        source_url=str(raw.source_url),
        content_hash=compute_content_hash(raw),
        raw_payload=raw_payload,
        fetched_at=utc_now(),
        is_hidden=is_hidden,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def create_admin_listing(
    db: Session,
    payload: AdminListingCreate,
    settings: Settings,
) -> Listing:
    provider = get_or_create_direct_provider(db, settings)
    owner_id = payload.owner_user_id
    external_id = (
        f"direct-{owner_id}-{uuid.uuid4().hex[:12]}"
        if owner_id is not None
        else f"direct-admin-{uuid.uuid4().hex[:12]}"
    )
    raw = RawListing(
        external_id=external_id,
        listing_type=payload.listing_type,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        country=payload.country,
        price=Decimal(str(payload.price)) if payload.price is not None else None,
        rooms=payload.rooms,
        property_type=payload.property_type,
        has_parking=payload.has_parking,
        job_category=payload.job_category,
        employment_type=payload.employment_type,
        workload_min=payload.workload_min,
        workload_max=payload.workload_max,
        source_url=str(payload.contact_url),
        raw_payload={"source": "admin", "owner_user_id": owner_id},
    )
    return _listing_from_raw(
        db,
        provider=provider,
        raw=raw,
        owner_user_id=owner_id,
        is_hidden=payload.is_hidden,
        raw_payload=raw.raw_payload,
    )


def update_admin_listing(db: Session, listing: Listing, payload: AdminListingUpdate) -> Listing:
    if payload.title is not None:
        listing.title = payload.title
    if payload.description is not None:
        listing.description = payload.description or None
    if payload.location is not None:
        listing.location = payload.location
    if payload.contact_url is not None:
        listing.source_url = payload.contact_url
    if payload.price is not None:
        listing.price = Decimal(str(payload.price))
    if payload.listing_type is not None:
        listing.listing_type = payload.listing_type
    if payload.is_hidden is not None:
        listing.is_hidden = payload.is_hidden

    raw = RawListing(
        external_id=listing.external_id,
        listing_type=listing.listing_type,
        title=listing.title,
        description=listing.description,
        location=listing.location or "",
        country=listing.country,
        price=listing.price,
        rooms=listing.rooms,
        property_type=listing.property_type,
        has_parking=listing.has_parking,
        job_category=listing.job_category,
        employment_type=listing.employment_type,
        workload_min=listing.workload_min,
        workload_max=listing.workload_max,
        source_url=listing.source_url,
        raw_payload=listing.raw_payload or {},
    )
    listing.content_hash = compute_content_hash(raw)
    listing.fetched_at = utc_now()
    db.commit()
    db.refresh(listing)
    return listing

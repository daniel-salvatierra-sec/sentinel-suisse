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
        source_url=payload.contact_url,
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

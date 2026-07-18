"""Upsert listings with deduplication."""

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.ingest.hashing import compute_content_hash, utc_now
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.provider import Provider


@dataclass
class IngestStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    created_listing_ids: list[int] = field(default_factory=list)


class IngestService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_listings(self, provider_slug: str, items: list[RawListing]) -> IngestStats:
        provider = self.db.scalar(select(Provider).where(Provider.slug == provider_slug))
        if provider is None:
            msg = f"Provider not found: {provider_slug}"
            raise ValueError(msg)

        stats = IngestStats()
        fetched_at = utc_now()

        for item in items:
            content_hash = compute_content_hash(item)
            existing = self.db.scalar(
                select(Listing).where(
                    Listing.provider_id == provider.id,
                    Listing.external_id == item.external_id,
                )
            )

            if existing is None:
                listing = Listing(
                    provider_id=provider.id,
                    external_id=item.external_id,
                    listing_type=item.listing_type,
                    title=item.title,
                    description=item.description,
                    location=item.location,
                    price=item.price,
                    rooms=item.rooms,
                    property_type=item.property_type,
                    has_parking=item.has_parking,
                    job_category=item.job_category,
                    employment_type=item.employment_type,
                    workload_min=item.workload_min,
                    workload_max=item.workload_max,
                    source_url=str(item.source_url),
                    content_hash=content_hash,
                    raw_payload=item.raw_payload,
                    fetched_at=fetched_at,
                )
                self.db.add(listing)
                self.db.flush()
                stats.created_listing_ids.append(listing.id)
                stats.created += 1
                continue

            if existing.content_hash == content_hash:
                stats.skipped += 1
                continue

            existing.title = item.title
            existing.description = item.description
            existing.location = item.location
            existing.price = item.price
            existing.rooms = item.rooms
            existing.property_type = item.property_type
            existing.has_parking = item.has_parking
            existing.job_category = item.job_category
            existing.employment_type = item.employment_type
            existing.workload_min = item.workload_min
            existing.workload_max = item.workload_max
            existing.source_url = str(item.source_url)
            existing.content_hash = content_hash
            existing.raw_payload = item.raw_payload
            existing.fetched_at = fetched_at
            stats.updated += 1

        self.db.commit()
        return stats

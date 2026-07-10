"""Upsert listings with deduplication."""

from dataclasses import dataclass

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
                self.db.add(
                    Listing(
                        provider_id=provider.id,
                        external_id=item.external_id,
                        listing_type=item.listing_type,
                        title=item.title,
                        description=item.description,
                        location=item.location,
                        price=item.price,
                        source_url=str(item.source_url),
                        content_hash=content_hash,
                        raw_payload=item.raw_payload,
                        fetched_at=fetched_at,
                    )
                )
                stats.created += 1
                continue

            if existing.content_hash == content_hash:
                stats.skipped += 1
                continue

            existing.title = item.title
            existing.description = item.description
            existing.location = item.location
            existing.price = item.price
            existing.source_url = str(item.source_url)
            existing.content_hash = content_hash
            existing.raw_payload = item.raw_payload
            existing.fetched_at = fetched_at
            stats.updated += 1

        self.db.commit()
        return stats

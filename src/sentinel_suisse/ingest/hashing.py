"""Ingestion utilities."""

import hashlib
import json
from datetime import UTC, datetime

from sentinel_suisse.ingest.schemas import RawListing


def compute_content_hash(listing: RawListing) -> str:
    """Stable SHA-256 hash for deduplication."""
    payload = {
        "external_id": listing.external_id,
        "title": listing.title,
        "description": listing.description,
        "location": listing.location,
        "price": str(listing.price) if listing.price is not None else None,
        "source_url": str(listing.source_url),
        "listing_type": listing.listing_type.value,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(UTC)

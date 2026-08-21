"""Hide listings that have not been seen in a recent ingest run."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import Select

from sentinel_suisse.config import get_settings
from sentinel_suisse.models.listing import Listing


def freshness_cutoff() -> datetime | None:
    hours = get_settings().listing_fresh_hours
    if hours <= 0:
        return None
    return datetime.now(UTC) - timedelta(hours=hours)


def listing_is_fresh(listing: Listing) -> bool:
    cutoff = freshness_cutoff()
    if cutoff is None:
        return True
    return listing.fetched_at >= cutoff


def apply_freshness_filter(stmt: Select[tuple[Listing]]) -> Select[tuple[Listing]]:
    cutoff = freshness_cutoff()
    if cutoff is None:
        return stmt
    return stmt.where(Listing.fetched_at >= cutoff)

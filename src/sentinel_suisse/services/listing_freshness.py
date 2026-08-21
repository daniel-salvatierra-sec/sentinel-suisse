"""Hide listings that have not been seen in a recent ingest run."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, or_

from sentinel_suisse.config import get_settings
from sentinel_suisse.models.listing import Listing


def freshness_cutoff() -> datetime | None:
    hours = get_settings().listing_fresh_hours
    if hours <= 0:
        return None
    return datetime.now(UTC) - timedelta(hours=hours)


def listing_is_fresh(listing: Listing) -> bool:
    if listing.owner_user_id is not None:
        return True
    cutoff = freshness_cutoff()
    if cutoff is None:
        return True
    return listing.fetched_at >= cutoff


def apply_freshness_filter(stmt: Select[tuple[Listing]]) -> Select[tuple[Listing]]:
    cutoff = freshness_cutoff()
    if cutoff is None:
        return stmt
    return stmt.where(or_(Listing.owner_user_id.is_not(None), Listing.fetched_at >= cutoff))

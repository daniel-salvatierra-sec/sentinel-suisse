"""Re-classify stored job listings after taxonomy improvements."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.ingest.hashing import compute_content_hash, listing_to_raw
from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.provider import Provider
from sentinel_suisse.services.job_taxonomy import classify_job_category


@dataclass
class JobReclassifyStats:
    scanned: int = 0
    changed: int = 0
    unchanged: int = 0


def proposed_job_category(stored_category: str | None, title: str | None) -> str | None:
    """Return the category we would store for this listing today."""
    return classify_job_category(stored_category, title)


def reclassify_job_listings(
    db: Session,
    *,
    provider_slug: str | None = None,
    dry_run: bool = False,
) -> JobReclassifyStats:
    """Refresh job_category (and content_hash) on existing job listings."""
    stmt = select(Listing).where(Listing.listing_type == ListingType.JOB)
    if provider_slug is not None:
        stmt = stmt.join(Provider).where(Provider.slug == provider_slug)

    stats = JobReclassifyStats()
    for listing in db.scalars(stmt):
        stats.scanned += 1
        new_category = proposed_job_category(listing.job_category, listing.title)
        if new_category == listing.job_category:
            stats.unchanged += 1
            continue

        stats.changed += 1
        if dry_run:
            continue

        listing.job_category = new_category
        listing.content_hash = compute_content_hash(listing_to_raw(listing))

    if not dry_run:
        db.commit()
    return stats

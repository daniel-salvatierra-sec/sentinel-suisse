"""Data retention maintenance tasks."""

import argparse
import logging
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import update

from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.services.job_reclassify import reclassify_job_listings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def purge_raw_payload(days: int) -> int:
    """Null out raw_payload on listings older than ``days`` (by fetched_at)."""
    cutoff = datetime.now(UTC) - timedelta(days=days)
    db = SessionLocal()
    try:
        stmt = (
            update(Listing)
            .where(Listing.fetched_at < cutoff, Listing.raw_payload.is_not(None))
            .values(raw_payload=None)
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount or 0
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sentinel Suisse maintenance tasks")
    sub = parser.add_subparsers(dest="command", required=True)

    purge = sub.add_parser(
        "purge-raw-payload",
        help="Clear raw_payload JSON on listings older than N days",
    )
    purge.add_argument(
        "--days",
        type=int,
        default=30,
        help="Retention window in days (default: 30)",
    )

    reclassify = sub.add_parser(
        "reclassify-jobs",
        help="Re-run job taxonomy on stored job listings",
    )
    reclassify.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Optional provider slug (e.g. jobup, jobs, adzuna)",
    )
    reclassify.add_argument(
        "--dry-run",
        action="store_true",
        help="Count changes without writing to the database",
    )

    args = parser.parse_args()

    if args.command == "purge-raw-payload":
        if args.days < 1:
            print("--days must be at least 1", file=sys.stderr)
            sys.exit(1)
        count = purge_raw_payload(args.days)
        logger.info("Purged raw_payload on %s listing(s) older than %s days", count, args.days)
        print(f"purged={count}")
        return

    if args.command == "reclassify-jobs":
        db = SessionLocal()
        try:
            stats = reclassify_job_listings(
                db,
                provider_slug=args.provider,
                dry_run=args.dry_run,
            )
        finally:
            db.close()
        mode = "dry-run" if args.dry_run else "applied"
        logger.info(
            "Reclassified jobs (%s): scanned=%s changed=%s unchanged=%s",
            mode,
            stats.scanned,
            stats.changed,
            stats.unchanged,
        )
        print(
            f"mode={mode} scanned={stats.scanned} "
            f"changed={stats.changed} unchanged={stats.unchanged}"
        )


if __name__ == "__main__":
    main()

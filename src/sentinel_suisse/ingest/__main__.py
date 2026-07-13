"""Ingestion CLI."""

import argparse
import sys
from pathlib import Path

from sentinel_suisse.config import get_settings
from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.ingest.connectors.fixture import load_fixture
from sentinel_suisse.ingest.connectors.homegate import (
    HomegateDisabledError,
    HomegateFetchError,
    fetch_search_listings,
)
from sentinel_suisse.ingest.service import IngestService
from sentinel_suisse.services.alerts import AlertService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest listings into Sentinel Suisse")
    parser.add_argument(
        "--provider",
        required=True,
        help="Provider slug (e.g. homegate)",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--fixture",
        type=Path,
        help="Path to JSON fixture file (pilot / tests)",
    )
    source.add_argument(
        "--live",
        action="store_true",
        help="Fetch from Homegate search page (requires INGEST_HOMEGATE_LIVE=true)",
    )
    parser.add_argument(
        "--search-url",
        type=str,
        default=None,
        help="Override Homegate search URL (with --live)",
    )
    parser.add_argument(
        "--dispatch-alerts",
        action="store_true",
        help="Dispatch alerts for newly created listings after ingest",
    )
    args = parser.parse_args()

    settings = get_settings()
    dispatch_alerts = args.dispatch_alerts or settings.ingest_dispatch_alerts

    try:
        if args.fixture is not None:
            items = load_fixture(args.fixture)
        else:
            items = fetch_search_listings(settings, search_url=args.search_url)
    except (HomegateDisabledError, HomegateFetchError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        stats = IngestService(db).upsert_listings(args.provider, items)
        if dispatch_alerts and stats.created_listing_ids:
            alert_service = AlertService(db)
            for listing_id in stats.created_listing_ids:
                alert_stats = alert_service.dispatch_for_listing(listing_id)
                print(
                    f"  alerts listing_id={listing_id}: "
                    f"matched={alert_stats.matched} sent={alert_stats.sent} "
                    f"skipped={alert_stats.skipped} failed={alert_stats.failed}"
                )
    finally:
        db.close()

    print(f"Ingest complete for provider={args.provider!r}")
    print(f"  created={stats.created} updated={stats.updated} skipped={stats.skipped}")


if __name__ == "__main__":
    main()

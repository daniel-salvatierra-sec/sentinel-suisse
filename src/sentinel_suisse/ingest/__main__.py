"""Ingestion CLI."""

import argparse
from pathlib import Path

from sentinel_suisse.config import get_settings
from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.ingest.connectors.fixture import load_fixture
from sentinel_suisse.ingest.service import IngestService
from sentinel_suisse.services.alerts import AlertService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest listings into Sentinel Suisse")
    parser.add_argument(
        "--provider",
        required=True,
        help="Provider slug (e.g. homegate)",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        required=True,
        help="Path to JSON fixture file",
    )
    parser.add_argument(
        "--dispatch-alerts",
        action="store_true",
        help="Dispatch alerts for newly created listings after ingest",
    )
    args = parser.parse_args()

    settings = get_settings()
    dispatch_alerts = args.dispatch_alerts or settings.ingest_dispatch_alerts

    items = load_fixture(args.fixture)
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

"""Ingestion CLI."""

import argparse
import sys
from pathlib import Path

from sentinel_suisse.config import get_settings
from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.ingest.connectors.anibis import (
    AnibisDisabledError,
    AnibisFetchError,
)
from sentinel_suisse.ingest.connectors.anibis import (
    fetch_search_listings as fetch_anibis_listings,
)
from sentinel_suisse.ingest.connectors.fixture import load_fixture
from sentinel_suisse.ingest.connectors.flatfox import (
    FlatfoxDisabledError,
    FlatfoxFetchError,
)
from sentinel_suisse.ingest.connectors.flatfox import (
    fetch_search_listings as fetch_flatfox_listings,
)
from sentinel_suisse.ingest.connectors.homegate import (
    HomegateDisabledError,
    HomegateFetchError,
)
from sentinel_suisse.ingest.connectors.homegate import (
    fetch_search_listings as fetch_homegate_listings,
)
from sentinel_suisse.ingest.connectors.immoscout import (
    ImmoscoutDisabledError,
    ImmoscoutFetchError,
)
from sentinel_suisse.ingest.connectors.immoscout import (
    fetch_search_listings as fetch_immoscout_listings,
)
from sentinel_suisse.ingest.connectors.indeed_fr import (
    IndeedFrDisabledError,
    IndeedFrFetchError,
)
from sentinel_suisse.ingest.connectors.indeed_fr import (
    fetch_search_listings as fetch_indeed_fr_listings,
)
from sentinel_suisse.ingest.connectors.jobs import (
    JobsDisabledError,
    JobsFetchError,
)
from sentinel_suisse.ingest.connectors.jobs import (
    fetch_search_listings as fetch_jobs_listings,
)
from sentinel_suisse.ingest.connectors.jobup import (
    JobupDisabledError,
    JobupFetchError,
)
from sentinel_suisse.ingest.connectors.jobup import (
    fetch_search_listings as fetch_jobup_listings,
)
from sentinel_suisse.ingest.connectors.leboncoin import (
    LeboncoinDisabledError,
    LeboncoinFetchError,
)
from sentinel_suisse.ingest.connectors.leboncoin import (
    fetch_search_listings as fetch_leboncoin_listings,
)
from sentinel_suisse.ingest.connectors.newhome import (
    NewhomeDisabledError,
    NewhomeFetchError,
)
from sentinel_suisse.ingest.connectors.newhome import (
    fetch_search_listings as fetch_newhome_listings,
)
from sentinel_suisse.ingest.service import IngestService
from sentinel_suisse.services.alerts import AlertService

_LIVE_CONNECTORS = {
    "homegate": fetch_homegate_listings,
    "jobs": fetch_jobs_listings,
    "flatfox": fetch_flatfox_listings,
    "immoscout": fetch_immoscout_listings,
    "newhome": fetch_newhome_listings,
    "anibis": fetch_anibis_listings,
    "jobup": fetch_jobup_listings,
    "leboncoin": fetch_leboncoin_listings,
    "indeed-fr": fetch_indeed_fr_listings,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest listings into Sentinel Suisse")
    parser.add_argument(
        "--provider",
        required=True,
        help="Provider slug (e.g. homegate, leboncoin, indeed-fr)",
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
        help="Fetch live from provider search page (opt-in via .env)",
    )
    parser.add_argument(
        "--search-url",
        type=str,
        default=None,
        help="Override provider search URL (with --live)",
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
            fetcher = _LIVE_CONNECTORS.get(args.provider)
            if fetcher is None:
                msg = f"Live ingest not supported for provider: {args.provider}"
                raise ValueError(msg)
            items = fetcher(settings, search_url=args.search_url)
    except (
        HomegateDisabledError,
        HomegateFetchError,
        JobsDisabledError,
        JobsFetchError,
        FlatfoxDisabledError,
        FlatfoxFetchError,
        ImmoscoutDisabledError,
        ImmoscoutFetchError,
        NewhomeDisabledError,
        NewhomeFetchError,
        AnibisDisabledError,
        AnibisFetchError,
        JobupDisabledError,
        JobupFetchError,
        LeboncoinDisabledError,
        LeboncoinFetchError,
        IndeedFrDisabledError,
        IndeedFrFetchError,
        ValueError,
    ) as exc:
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

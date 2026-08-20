"""Logitech (Lausanne HQ) — Workday CXS JSON API, no scraping.

The company's public careers portal (logitech.wd5.myworkdayjobs.com/Logitech) is the
same Workday Candidate Experience app used by Richemont and Lombard Odier.
See docs/providers/logitech.md.
"""

from typing import Any

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.workday import (
    WorkdayFetchError,
    WorkdaySite,
    fetch_workday_listings,
)
from sentinel_suisse.ingest.connectors.workday import (
    parse_search_page as parse_workday_search_page,
)
from sentinel_suisse.ingest.connectors.workday import (
    pick_candidate_location_ids as pick_workday_location_ids,
)
from sentinel_suisse.ingest.schemas import RawListing

LOGITECH_SITE = WorkdaySite(
    slug="logitech",
    tenant="logitech",
    shard="wd5",
    site="Logitech",
)


class LogitechFetchError(WorkdayFetchError):
    """Logitech Workday API HTTP or parse failure."""


class LogitechDisabledError(RuntimeError):
    """Live Logitech ingest is not enabled in settings."""


def parse_search_page(payload: dict[str, Any], settings: Settings) -> list[RawListing]:
    return parse_workday_search_page(payload, settings, LOGITECH_SITE, error_cls=LogitechFetchError)


def pick_candidate_location_ids(payload: dict[str, Any], settings: Settings) -> list[str]:
    return pick_workday_location_ids(
        payload,
        extra_location_hints=settings.logitech_extra_location_hints,
        error_cls=LogitechFetchError,
    )


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query Logitech's Workday CXS API. `search_url` unused — CLI signature."""
    if not settings.ingest_logitech_live:
        msg = "Live Logitech ingest is disabled (set INGEST_LOGITECH_LIVE=true)"
        raise LogitechDisabledError(msg)

    return fetch_workday_listings(
        settings,
        LOGITECH_SITE,
        extra_location_hints=settings.logitech_extra_location_hints,
        error_cls=LogitechFetchError,
    )

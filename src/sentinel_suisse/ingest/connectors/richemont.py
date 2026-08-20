"""Richemont (luxury goods group) — Workday CXS JSON API, no scraping.

Thin wrapper around the shared Workday client. Tenant/site taken from the public
career URL careers.richemont.com → richemont.wd3.myworkdayjobs.com/broadbean_external.
See docs/providers/richemont.md and connectors/workday.py.
"""

from typing import Any

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.workday import (
    WorkdayFetchError,
    WorkdaySite,
    fetch_workday_listings,
    pick_employment_type,
    strip_html,
)
from sentinel_suisse.ingest.connectors.workday import (
    parse_search_page as parse_workday_search_page,
)
from sentinel_suisse.ingest.connectors.workday import (
    pick_candidate_location_ids as pick_workday_location_ids,
)
from sentinel_suisse.ingest.schemas import RawListing

RICHEMONT_SITE = WorkdaySite(
    slug="richemont",
    tenant="richemont",
    shard="wd3",
    site="broadbean_external",
)

# Re-exported so existing tests keep importing from this module.
_strip_html = strip_html
_pick_employment_type = pick_employment_type


class RichemontFetchError(WorkdayFetchError):
    """Richemont Workday API HTTP or parse failure."""


class RichemontDisabledError(RuntimeError):
    """Live Richemont ingest is not enabled in settings."""


def parse_search_page(payload: dict[str, Any], settings: Settings) -> list[RawListing]:
    return parse_workday_search_page(
        payload, settings, RICHEMONT_SITE, error_cls=RichemontFetchError
    )


def pick_candidate_location_ids(payload: dict[str, Any], settings: Settings) -> list[str]:
    return pick_workday_location_ids(
        payload,
        extra_location_hints=settings.richemont_extra_location_hints,
        error_cls=RichemontFetchError,
    )


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query Richemont's Workday CXS API. `search_url` unused — kept for CLI signature."""
    if not settings.ingest_richemont_live:
        msg = "Live Richemont ingest is disabled (set INGEST_RICHEMONT_LIVE=true)"
        raise RichemontDisabledError(msg)

    return fetch_workday_listings(
        settings,
        RICHEMONT_SITE,
        extra_location_hints=settings.richemont_extra_location_hints,
        error_cls=RichemontFetchError,
    )

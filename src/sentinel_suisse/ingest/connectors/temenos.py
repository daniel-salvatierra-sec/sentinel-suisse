"""Temenos (Geneva HQ) — Workday CXS JSON API, no scraping.

The company's public careers portal (temenos.wd103.myworkdayjobs.com/Temenoscareers)
is the same Workday Candidate Experience app used by Richemont, Lombard Odier,
Logitech, and P&G. See docs/providers/temenos.md.
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

TEMENOS_SITE = WorkdaySite(
    slug="temenos",
    tenant="temenos",
    shard="wd103",
    site="Temenoscareers",
)


class TemenosFetchError(WorkdayFetchError):
    """Temenos Workday API HTTP or parse failure."""


class TemenosDisabledError(RuntimeError):
    """Live Temenos ingest is not enabled in settings."""


def parse_search_page(payload: dict[str, Any], settings: Settings) -> list[RawListing]:
    return parse_workday_search_page(payload, settings, TEMENOS_SITE, error_cls=TemenosFetchError)


def pick_candidate_location_ids(payload: dict[str, Any], settings: Settings) -> list[str]:
    return pick_workday_location_ids(
        payload,
        extra_location_hints=settings.temenos_extra_location_hints,
        error_cls=TemenosFetchError,
    )


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query Temenos's Workday CXS API. `search_url` unused — CLI signature."""
    if not settings.ingest_temenos_live:
        msg = "Live Temenos ingest is disabled (set INGEST_TEMENOS_LIVE=true)"
        raise TemenosDisabledError(msg)

    return fetch_workday_listings(
        settings,
        TEMENOS_SITE,
        extra_location_hints=settings.temenos_extra_location_hints,
        error_cls=TemenosFetchError,
    )

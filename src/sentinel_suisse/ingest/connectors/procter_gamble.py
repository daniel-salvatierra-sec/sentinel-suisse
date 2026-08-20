"""Procter & Gamble (Geneva European HQ) — Workday CXS JSON API, no scraping.

P&G's public careers portal (pg.wd5.myworkdayjobs.com/1000) is the same Workday
Candidate Experience app used by Richemont, Lombard Odier, and Logitech.
See docs/providers/procter-gamble.md.
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

PROCTER_GAMBLE_SITE = WorkdaySite(
    slug="procter-gamble",
    tenant="pg",
    shard="wd5",
    site="1000",
)


class ProcterGambleFetchError(WorkdayFetchError):
    """P&G Workday API HTTP or parse failure."""


class ProcterGambleDisabledError(RuntimeError):
    """Live P&G ingest is not enabled in settings."""


def parse_search_page(payload: dict[str, Any], settings: Settings) -> list[RawListing]:
    return parse_workday_search_page(
        payload, settings, PROCTER_GAMBLE_SITE, error_cls=ProcterGambleFetchError
    )


def pick_candidate_location_ids(payload: dict[str, Any], settings: Settings) -> list[str]:
    return pick_workday_location_ids(
        payload,
        extra_location_hints=settings.procter_gamble_extra_location_hints,
        error_cls=ProcterGambleFetchError,
    )


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query P&G's Workday CXS API. `search_url` unused — CLI signature."""
    if not settings.ingest_procter_gamble_live:
        msg = "Live P&G ingest is disabled (set INGEST_PROCTER_GAMBLE_LIVE=true)"
        raise ProcterGambleDisabledError(msg)

    return fetch_workday_listings(
        settings,
        PROCTER_GAMBLE_SITE,
        extra_location_hints=settings.procter_gamble_extra_location_hints,
        error_cls=ProcterGambleFetchError,
    )

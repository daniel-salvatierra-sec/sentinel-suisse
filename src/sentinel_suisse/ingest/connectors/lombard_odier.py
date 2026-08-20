"""Lombard Odier (Geneva private bank) — Workday CXS JSON API, no scraping.

The bank's public careers portal (lombardodier.wd3.myworkdayjobs.com) is the same
Workday Candidate Experience app used by Richemont. See docs/providers/lombard-odier.md.
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

LOMBARD_ODIER_SITE = WorkdaySite(
    slug="lombard-odier",
    tenant="lombardodier",
    shard="wd3",
    site="Lombard_Odier_Careers",
)


class LombardOdierFetchError(WorkdayFetchError):
    """Lombard Odier Workday API HTTP or parse failure."""


class LombardOdierDisabledError(RuntimeError):
    """Live Lombard Odier ingest is not enabled in settings."""


def parse_search_page(payload: dict[str, Any], settings: Settings) -> list[RawListing]:
    return parse_workday_search_page(
        payload, settings, LOMBARD_ODIER_SITE, error_cls=LombardOdierFetchError
    )


def pick_candidate_location_ids(payload: dict[str, Any], settings: Settings) -> list[str]:
    return pick_workday_location_ids(
        payload,
        extra_location_hints=settings.lombard_odier_extra_location_hints,
        error_cls=LombardOdierFetchError,
    )


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query Lombard Odier's Workday CXS API. `search_url` unused — CLI signature."""
    if not settings.ingest_lombard_odier_live:
        msg = "Live Lombard Odier ingest is disabled (set INGEST_LOMBARD_ODIER_LIVE=true)"
        raise LombardOdierDisabledError(msg)

    return fetch_workday_listings(
        settings,
        LOMBARD_ODIER_SITE,
        extra_location_hints=settings.lombard_odier_extra_location_hints,
        error_cls=LombardOdierFetchError,
    )

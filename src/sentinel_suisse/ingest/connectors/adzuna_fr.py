"""Adzuna France (Haute-Savoie / Geneva border) — same official API as Swiss Adzuna.

A second ingest pass against api.adzuna.com country=fr. Reuses ADZUNA_APP_ID / APP_KEY.
France Travail's developer portal is unreliable; this is the sanctioned substitute
for Annemasse / border jobs. See docs/providers/adzuna.md.
"""

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna import (
    fetch_search_listings as fetch_adzuna_listings,
)
from sentinel_suisse.ingest.schemas import RawListing

_BORDER_LOCATIONS = (
    "Haute-Savoie",
    "Annemasse",
    "Ferney-Voltaire",
    "Saint-Julien-en-Genevois",
    "Gaillard",
)


class AdzunaFrDisabledError(RuntimeError):
    """Live Adzuna France ingest is not enabled in settings."""


def _france_locations(settings: Settings) -> list[str]:
    primary = settings.adzuna_fr_location.strip()
    ordered: list[str] = []
    for item in (primary, *_BORDER_LOCATIONS):
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query Adzuna's France catalogue. `search_url` unused — CLI signature."""
    if not settings.ingest_adzuna_fr_live:
        msg = "Live Adzuna France ingest is disabled (set INGEST_ADZUNA_FR_LIVE=true)"
        raise AdzunaFrDisabledError(msg)

    seen: set[str] = set()
    parsed: list[RawListing] = []
    for location in _france_locations(settings):
        fr_settings = settings.model_copy(
            update={
                "ingest_adzuna_live": True,
                "adzuna_country": "fr",
                "adzuna_location": location,
                "adzuna_keywords": settings.adzuna_fr_keywords,
            }
        )
        for item in fetch_adzuna_listings(fr_settings, search_url=search_url):
            if item.external_id in seen:
                continue
            seen.add(item.external_id)
            parsed.append(item)
    return parsed

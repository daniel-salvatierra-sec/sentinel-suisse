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


class AdzunaFrDisabledError(RuntimeError):
    """Live Adzuna France ingest is not enabled in settings."""


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query Adzuna's France catalogue. `search_url` unused — CLI signature."""
    if not settings.ingest_adzuna_fr_live:
        msg = "Live Adzuna France ingest is disabled (set INGEST_ADZUNA_FR_LIVE=true)"
        raise AdzunaFrDisabledError(msg)

    fr_settings = settings.model_copy(
        update={
            "ingest_adzuna_live": True,
            "adzuna_country": "fr",
            "adzuna_location": settings.adzuna_fr_location,
            "adzuna_keywords": settings.adzuna_fr_keywords,
        }
    )
    return fetch_adzuna_listings(fr_settings, search_url=search_url)

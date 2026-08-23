"""Adzuna France (Haute-Savoie / Geneva border) — same official API as Swiss Adzuna.

A second ingest pass against api.adzuna.com country=fr. Reuses ADZUNA_APP_ID / APP_KEY.
France Travail's developer portal is unreliable; this is the sanctioned substitute
for Annemasse / border jobs. See docs/providers/adzuna.md.
"""

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna import fetch_country_locations
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
    ordered: list[str] = []
    for item in (settings.adzuna_fr_location.strip(), *_BORDER_LOCATIONS):
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query Adzuna's France catalogue. `search_url` unused — CLI signature."""
    return fetch_country_locations(
        settings,
        country="fr",
        locations=_france_locations(settings),
        enabled=settings.ingest_adzuna_fr_live,
        disabled_error=AdzunaFrDisabledError,
        disabled_message="Live Adzuna France ingest is disabled (set INGEST_ADZUNA_FR_LIVE=true)",
        keywords=settings.adzuna_fr_keywords,
        search_url=search_url,
    )

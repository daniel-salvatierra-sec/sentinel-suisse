"""Adzuna Italy — Swiss-Italian border towns plus cities over 500k.

Official API, same keys as CH. Not scraping.
"""

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna import fetch_country_locations
from sentinel_suisse.ingest.schemas import RawListing

_BORDER_LOCATIONS = (
    "Como",
    "Varese",
    "Domodossola",
)

# City-proper population over 500,000 (Istat). Local names for Adzuna `where`.
_INLAND_CITIES = (
    "Roma",
    "Milano",
    "Napoli",
    "Torino",
    "Palermo",
    "Genova",
)


class AdzunaItDisabledError(RuntimeError):
    """Live Adzuna Italy ingest is not enabled in settings."""


def _italy_locations(settings: Settings) -> list[str]:
    ordered: list[str] = []
    for item in (settings.adzuna_it_location.strip(), *_BORDER_LOCATIONS):
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def _inland_locations(border: list[str]) -> list[str]:
    return [city for city in _INLAND_CITIES if city not in border]


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    border = _italy_locations(settings)
    return fetch_country_locations(
        settings,
        country="it",
        locations=border,
        extra_locations=_inland_locations(border),
        enabled=settings.ingest_adzuna_it_live,
        disabled_error=AdzunaItDisabledError,
        disabled_message="Live Adzuna Italy ingest is disabled (set INGEST_ADZUNA_IT_LIVE=true)",
        keywords=settings.adzuna_it_keywords,
        search_url=search_url,
    )

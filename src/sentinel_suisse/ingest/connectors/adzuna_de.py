"""Adzuna Germany — Swiss-German border towns plus cities over 500k.

Official API, same keys as CH. Not scraping.
"""

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna import fetch_country_locations
from sentinel_suisse.ingest.schemas import RawListing

_BORDER_LOCATIONS = (
    "Lorrach",
    "Weil am Rhein",
    "Konstanz",
    "Waldshut",
)

# City-proper population over 500,000 (Destatis). Local names for Adzuna `where`.
_INLAND_CITIES = (
    "Berlin",
    "Hamburg",
    "München",
    "Köln",
    "Frankfurt",
    "Stuttgart",
    "Düsseldorf",
    "Leipzig",
    "Dortmund",
    "Essen",
    "Bremen",
    "Dresden",
    "Hannover",
    "Nürnberg",
    "Duisburg",
)


class AdzunaDeDisabledError(RuntimeError):
    """Live Adzuna Germany ingest is not enabled in settings."""


def _germany_locations(settings: Settings) -> list[str]:
    ordered: list[str] = []
    for item in (settings.adzuna_de_location.strip(), *_BORDER_LOCATIONS):
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def _inland_locations(border: list[str]) -> list[str]:
    return [city for city in _INLAND_CITIES if city not in border]


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    border = _germany_locations(settings)
    return fetch_country_locations(
        settings,
        country="de",
        locations=border,
        extra_locations=_inland_locations(border),
        enabled=settings.ingest_adzuna_de_live,
        disabled_error=AdzunaDeDisabledError,
        disabled_message="Live Adzuna Germany ingest is disabled (set INGEST_ADZUNA_DE_LIVE=true)",
        keywords=settings.adzuna_de_keywords,
        search_url=search_url,
    )

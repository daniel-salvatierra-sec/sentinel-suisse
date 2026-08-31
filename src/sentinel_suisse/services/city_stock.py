"""Which picker cities currently have fresh listings.

Keeps the full city catalog in the app; only the dropdown hides empty ones.
When ingest adds stock, the city reappears automatically.
"""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from sentinel_suisse.models.enums import CountryCode, ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.public_cities import CityStock
from sentinel_suisse.services.listing_freshness import apply_freshness_filter
from sentinel_suisse.services.location_match import expand_location_query

# Same order/names as frontend/src/swissCities.ts (matching + map pins stay there).
PICKER_CITIES: tuple[str, ...] = (
    "Geneva",
    "Zurich",
    "Bern",
    "Basel",
    "Lausanne",
    "Lugano",
    "Lucerne",
    "St. Gallen",
    "Winterthur",
    "Fribourg",
    "Neuchatel",
    "La Chaux-de-Fonds",
    "Biel",
    "Zug",
    "Sion",
    "Chur",
    "Bellinzona",
    "Schaffhausen",
    "Thun",
    "Aarau",
    "Nyon",
    "Morges",
    "Vevey",
    "Montreux",
    "Yverdon",
    "Bulle",
    "Martigny",
    "Sierre",
    "Monthey",
    "Delemont",
    "Olten",
    "Baden",
    "Wil",
    "Uster",
    "Frauenfeld",
    "Solothurn",
    "Langenthal",
    "Interlaken",
    "Liestal",
    "Kreuzlingen",
    "Locarno",
    "Mendrisio",
    "Chiasso",
    "Brig",
    "Schwyz",
    "Emmen",
    "Dietikon",
    "Horgen",
)

# Same names as frontend/src/zoneCities.ts. Border keys match expand_location_query.
NEIGHBOR_PICKER: tuple[tuple[CountryCode, str], ...] = (
    (CountryCode.FR, "FR-border"),
    (CountryCode.FR, "Paris"),
    (CountryCode.FR, "Marseille"),
    (CountryCode.FR, "Lyon"),
    (CountryCode.FR, "Toulouse"),
    (CountryCode.DE, "DE-border"),
    (CountryCode.DE, "Berlin"),
    (CountryCode.DE, "Hamburg"),
    (CountryCode.DE, "Munich"),
    (CountryCode.DE, "Cologne"),
    (CountryCode.DE, "Frankfurt"),
    (CountryCode.DE, "Stuttgart"),
    (CountryCode.DE, "Dusseldorf"),
    (CountryCode.DE, "Leipzig"),
    (CountryCode.DE, "Dortmund"),
    (CountryCode.DE, "Essen"),
    (CountryCode.DE, "Bremen"),
    (CountryCode.DE, "Dresden"),
    (CountryCode.DE, "Hanover"),
    (CountryCode.DE, "Nuremberg"),
    (CountryCode.DE, "Duisburg"),
    (CountryCode.IT, "IT-border"),
    (CountryCode.IT, "Rome"),
    (CountryCode.IT, "Milan"),
    (CountryCode.IT, "Naples"),
    (CountryCode.IT, "Turin"),
    (CountryCode.IT, "Palermo"),
    (CountryCode.IT, "Genoa"),
)

PICKER_ENTRIES: tuple[tuple[CountryCode, str], ...] = (
    tuple((CountryCode.CH, city) for city in PICKER_CITIES) + NEIGHBOR_PICKER
)


def _location_clause(city: str):
    terms = expand_location_query(city)
    if not terms:
        return None
    return or_(*[Listing.location.ilike(f"%{term}%") for term in terms])


def list_stocked_picker_cities(db: Session) -> list[CityStock]:
    """Cities with at least one fresh housing or job listing in that country."""
    stocked: list[CityStock] = []
    for country, city in PICKER_ENTRIES:
        location_match = _location_clause(city)
        if location_match is None:
            continue
        stmt = (
            select(Listing.listing_type, func.count())
            .where(
                Listing.is_hidden.is_(False),
                Listing.country == country,
                location_match,
            )
            .group_by(Listing.listing_type)
        )
        stmt = apply_freshness_filter(stmt)
        counts = {row[0]: int(row[1]) for row in db.execute(stmt)}
        housing = counts.get(ListingType.HOUSING, 0)
        jobs = counts.get(ListingType.JOB, 0)
        total = housing + jobs
        if total <= 0:
            continue
        stocked.append(
            CityStock(
                city=city,
                country=country,
                housing_count=housing,
                job_count=jobs,
                total=total,
            )
        )
    return stocked

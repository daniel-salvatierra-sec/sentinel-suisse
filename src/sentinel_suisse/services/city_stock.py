"""Which Swiss picker cities currently have fresh listings.

Keeps the full city catalog in the app; only the dropdown hides empty ones.
When ingest adds stock, the city reappears automatically.
"""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from sentinel_suisse.models.enums import ListingType
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


def _location_clause(city: str):
    terms = expand_location_query(city)
    if not terms:
        return None
    return or_(*[Listing.location.ilike(f"%{term}%") for term in terms])


def _count_type(db: Session, city: str, listing_type: ListingType) -> int:
    location_match = _location_clause(city)
    if location_match is None:
        return 0
    stmt = (
        select(func.count())
        .select_from(Listing)
        .where(
            Listing.is_hidden.is_(False),
            Listing.listing_type == listing_type,
            location_match,
        )
    )
    stmt = apply_freshness_filter(stmt)
    return int(db.scalar(stmt) or 0)


def list_stocked_picker_cities(db: Session) -> list[CityStock]:
    """Cities with at least one fresh housing or job listing.

    Uses a cheap existence probe first, then counts only stocked cities.
    """
    stocked: list[CityStock] = []
    for city in PICKER_CITIES:
        location_match = _location_clause(city)
        if location_match is None:
            continue
        probe = select(Listing.id).where(Listing.is_hidden.is_(False), location_match).limit(1)
        probe = apply_freshness_filter(probe)
        if db.scalar(probe) is None:
            continue
        housing = _count_type(db, city, ListingType.HOUSING)
        jobs = _count_type(db, city, ListingType.JOB)
        total = housing + jobs
        if total <= 0:
            continue
        stocked.append(
            CityStock(
                city=city,
                housing_count=housing,
                job_count=jobs,
                total=total,
            )
        )
    return stocked

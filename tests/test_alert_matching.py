"""Listing-to-search matching rules."""

from datetime import UTC, datetime
from decimal import Decimal

from sentinel_suisse.models.enums import EmploymentType, ListingType, PropertyType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.matching import listing_matches_query


def _sample_listing(
    *,
    location: str = "Geneva",
    price: str = "2400",
    listing_type: ListingType = ListingType.HOUSING,
    rooms: str | None = None,
    property_type: PropertyType | None = None,
    has_parking: bool | None = None,
    job_category: str | None = None,
    employment_type: EmploymentType | None = None,
    workload_min: int | None = None,
    workload_max: int | None = None,
) -> Listing:
    return Listing(
        id=1,
        provider_id=1,
        external_id="x",
        listing_type=listing_type,
        title="Apartment",
        location=location,
        price=Decimal(price) if listing_type == ListingType.HOUSING else None,
        rooms=Decimal(rooms) if rooms is not None else None,
        property_type=property_type,
        has_parking=has_parking,
        job_category=job_category,
        employment_type=employment_type,
        workload_min=workload_min,
        workload_max=workload_max,
        source_url="https://example.com/1",
        content_hash="a" * 64,
        fetched_at=datetime.now(UTC),
    )


def test_listing_matches_location_and_type() -> None:
    listing = _sample_listing(location="Geneva", price="2400")
    filters = SearchQuery(location="Geneva", listing_type=ListingType.HOUSING)
    assert listing_matches_query(listing, filters) is True


def test_listing_rejects_wrong_location() -> None:
    listing = _sample_listing(location="Lausanne", price="1200")
    filters = SearchQuery(location="Geneva", listing_type=ListingType.HOUSING)
    assert listing_matches_query(listing, filters) is False


def test_rooms_min_null_safe() -> None:
    listing = _sample_listing(rooms=None)
    filters = SearchQuery(rooms_min=Decimal("2.5"))
    assert listing_matches_query(listing, filters) is True


def test_rooms_min_rejects_smaller() -> None:
    listing = _sample_listing(rooms="1.5")
    filters = SearchQuery(rooms_min=Decimal("2.5"))
    assert listing_matches_query(listing, filters) is False


def test_property_type_and_parking() -> None:
    listing = _sample_listing(property_type=PropertyType.STUDIO, has_parking=False)
    assert listing_matches_query(listing, SearchQuery(property_type=PropertyType.STUDIO)) is True
    assert listing_matches_query(listing, SearchQuery(has_parking=True)) is False
    assert listing_matches_query(listing, SearchQuery(has_parking=False)) is True


def test_job_filters() -> None:
    listing = _sample_listing(
        listing_type=ListingType.JOB,
        job_category="healthcare",
        employment_type=EmploymentType.TEMPORARY,
        workload_min=80,
        workload_max=100,
    )
    assert (
        listing_matches_query(
            listing,
            SearchQuery(
                listing_type=ListingType.JOB,
                job_category="healthcare",
                employment_type=EmploymentType.TEMPORARY,
                workload_min=80,
                workload_max=100,
            ),
        )
        is True
    )
    assert (
        listing_matches_query(
            listing,
            SearchQuery(job_category="it", employment_type=EmploymentType.PERMANENT),
        )
        is False
    )
    assert listing_matches_query(listing, SearchQuery(workload_min=40, workload_max=60)) is False


def test_provider_ids_filter() -> None:
    listing = _sample_listing()
    assert listing_matches_query(listing, SearchQuery(provider_ids=[1, 2])) is True
    assert listing_matches_query(listing, SearchQuery(provider_ids=[9])) is False

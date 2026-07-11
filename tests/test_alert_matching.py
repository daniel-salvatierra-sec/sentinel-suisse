"""Listing-to-search matching rules."""

from datetime import UTC, datetime
from decimal import Decimal

from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.matching import listing_matches_query


def _sample_listing(*, location: str, price: str) -> Listing:
    return Listing(
        id=1,
        provider_id=1,
        external_id="x",
        listing_type=ListingType.HOUSING,
        title="Apartment",
        location=location,
        price=Decimal(price),
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

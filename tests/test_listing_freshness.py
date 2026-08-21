"""Listing freshness cutoff (stale ads drop out of search)."""

from datetime import UTC, datetime, timedelta

from sentinel_suisse.config import get_settings
from sentinel_suisse.models.enums import CountryCode, ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.services.listing_freshness import listing_is_fresh


def test_recent_listing_is_fresh() -> None:
    listing = Listing(
        id=1,
        provider_id=1,
        external_id="x",
        listing_type=ListingType.HOUSING,
        title="A",
        country=CountryCode.CH,
        source_url="https://example.com/1",
        content_hash="a" * 64,
        fetched_at=datetime.now(UTC),
    )
    assert listing_is_fresh(listing) is True


def test_owned_listing_stays_fresh_when_old() -> None:
    hours = get_settings().listing_fresh_hours
    listing = Listing(
        id=1,
        provider_id=1,
        owner_user_id=9,
        external_id="x",
        listing_type=ListingType.HOUSING,
        title="A",
        country=CountryCode.CH,
        source_url="https://example.com/1",
        content_hash="a" * 64,
        fetched_at=datetime.now(UTC) - timedelta(hours=hours + 1),
    )
    assert listing_is_fresh(listing) is True


def test_old_listing_is_stale() -> None:
    hours = get_settings().listing_fresh_hours
    listing = Listing(
        id=2,
        provider_id=1,
        external_id="y",
        listing_type=ListingType.HOUSING,
        title="B",
        country=CountryCode.CH,
        source_url="https://example.com/2",
        content_hash="b" * 64,
        fetched_at=datetime.now(UTC) - timedelta(hours=hours + 1),
    )
    assert listing_is_fresh(listing) is False

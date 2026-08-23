"""Flatfox public JSON connector tests (no live network)."""

import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.flatfox import (
    FlatfoxDisabledError,
    _format_location,
    fetch_search_listings,
    map_public_listing,
    parse_pin_list,
)
from sentinel_suisse.models.enums import CountryCode

_FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "flatfox_api_sample.json").read_text(
        encoding="utf-8"
    )
)


def test_parse_pin_list_skips_cheap_parking() -> None:
    pks = parse_pin_list(_FIXTURE["pins"])
    assert pks == [86294651]


def test_map_apartment_from_public_json() -> None:
    listing = map_public_listing(_FIXTURE["detail_apartment"])
    assert listing is not None
    assert listing.external_id == "86294651"
    assert listing.listing_type == "housing"
    assert listing.location == "Les Acacias, 1227"
    assert listing.rooms == Decimal("2.5")
    assert listing.has_parking is True
    assert str(listing.source_url).endswith("/86294651/")


def test_format_location_does_not_force_geneva() -> None:
    assert _format_location("Zürich", "8001", CountryCode.CH) == "Zurich, 8001"
    assert _format_location("Olten", "4600", CountryCode.CH) == "Olten, 4600"
    assert _format_location("Annemasse", "74100", CountryCode.FR) == "Annemasse, 74100, FR"


def test_map_skips_parking_category() -> None:
    assert map_public_listing(_FIXTURE["detail_parking"]) is None


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_flatfox_live=False)
    with pytest.raises(FlatfoxDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.flatfox.httpx.get")
def test_fetch_pins_then_details(mock_get: MagicMock) -> None:
    pin_response = MagicMock()
    pin_response.json.return_value = _FIXTURE["pins"]
    pin_response.raise_for_status = MagicMock()
    detail_response = MagicMock()
    detail_response.json.return_value = _FIXTURE["detail_apartment"]
    detail_response.raise_for_status = MagicMock()
    mock_get.side_effect = [pin_response, detail_response]

    settings = Settings(
        ingest_flatfox_live=True,
        ingest_rate_limit_seconds=0,
        flatfox_regions="geneva",
    )
    listings = fetch_search_listings(settings)
    assert len(listings) == 1
    assert listings[0].external_id == "86294651"
    assert mock_get.call_count == 2


@patch("sentinel_suisse.ingest.connectors.flatfox.httpx.get")
def test_fetch_walks_named_regions(mock_get: MagicMock) -> None:
    pin_response = MagicMock()
    pin_response.json.return_value = _FIXTURE["pins"]
    pin_response.raise_for_status = MagicMock()
    detail_response = MagicMock()
    detail_response.json.return_value = _FIXTURE["detail_apartment"]
    detail_response.raise_for_status = MagicMock()
    mock_get.side_effect = [pin_response, detail_response, pin_response]

    listings = fetch_search_listings(
        Settings(
            ingest_flatfox_live=True,
            ingest_rate_limit_seconds=0,
            flatfox_regions="geneva,zurich",
            flatfox_max_per_region=1,
            flatfox_max_listings=1,
        )
    )
    assert len(listings) == 1
    pin_urls = [
        call.kwargs.get("params") for call in mock_get.call_args_list if call.kwargs.get("params")
    ]
    assert any(params.get("west") == "5.95" for params in pin_urls)

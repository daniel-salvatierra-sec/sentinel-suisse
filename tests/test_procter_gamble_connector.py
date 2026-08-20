"""Procter & Gamble connector tests (Workday CXS, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.procter_gamble import (
    ProcterGambleDisabledError,
    fetch_search_listings,
    parse_search_page,
)
from sentinel_suisse.models.enums import CountryCode, EmploymentType

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
_FACETS_FIXTURE = _FIXTURES / "richemont_facets_sample.json"
_SEARCH_FIXTURE = _FIXTURES / "richemont_search_sample.json"
_DETAIL_GENEVA_FIXTURE = _FIXTURES / "richemont_detail_geneva_sample.json"
_DETAIL_PARIS_FIXTURE = _FIXTURES / "richemont_detail_paris_sample.json"


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_procter_gamble_live=False)
    with pytest.raises(ProcterGambleDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.workday.httpx.get")
def test_parse_maps_slug_and_geneva_country(mock_get: MagicMock) -> None:
    search_payload = json.loads(_SEARCH_FIXTURE.read_text(encoding="utf-8"))
    geneva_detail = json.loads(_DETAIL_GENEVA_FIXTURE.read_text(encoding="utf-8"))
    paris_detail = json.loads(_DETAIL_PARIS_FIXTURE.read_text(encoding="utf-8"))

    def _side_effect(url: str, **_kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = geneva_detail if "GENEVA" in url else paris_detail
        assert "pg.wd5.myworkdayjobs.com" in url
        return response

    mock_get.side_effect = _side_effect

    settings = Settings(ingest_rate_limit_seconds=0)
    listings = parse_search_page(search_payload, settings)

    assert len(listings) == 2
    geneva_listing = listings[0]
    assert geneva_listing.external_id == "procter-gamble-JR129879"
    assert geneva_listing.country == CountryCode.CH
    assert geneva_listing.employment_type == EmploymentType.INTERNSHIP
    assert geneva_listing.raw_payload["source"] == "procter-gamble"
    assert listings[1].country == CountryCode.FR


@patch("sentinel_suisse.ingest.connectors.workday.httpx.get")
@patch("sentinel_suisse.ingest.connectors.workday.httpx.post")
def test_fetch_search_listings_end_to_end(mock_post: MagicMock, mock_get: MagicMock) -> None:
    facets_payload = json.loads(_FACETS_FIXTURE.read_text(encoding="utf-8"))
    search_payload = json.loads(_SEARCH_FIXTURE.read_text(encoding="utf-8"))
    geneva_detail = json.loads(_DETAIL_GENEVA_FIXTURE.read_text(encoding="utf-8"))
    paris_detail = json.loads(_DETAIL_PARIS_FIXTURE.read_text(encoding="utf-8"))

    call_count = {"n": 0}

    def _post_side_effect(url: str, **kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        assert "pg.wd5.myworkdayjobs.com" in url
        assert "/1000/jobs" in url
        call_count["n"] += 1
        if call_count["n"] == 1:
            response.json.return_value = facets_payload
        else:
            assert kwargs.get("json", {}).get("appliedFacets", {}).get("locations")
            response.json.return_value = search_payload
        return response

    mock_post.side_effect = _post_side_effect

    def _get_side_effect(url: str, **_kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = geneva_detail if "GENEVA" in url else paris_detail
        return response

    mock_get.side_effect = _get_side_effect

    settings = Settings(ingest_procter_gamble_live=True, ingest_rate_limit_seconds=0)
    listings = fetch_search_listings(settings)

    assert len(listings) == 2
    assert {listing.country for listing in listings} == {CountryCode.CH, CountryCode.FR}
    assert mock_post.call_count == 2

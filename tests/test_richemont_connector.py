"""Richemont connector tests (Workday CXS public JSON API, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.richemont import (
    RichemontDisabledError,
    RichemontFetchError,
    _pick_employment_type,
    _strip_html,
    fetch_search_listings,
    parse_search_page,
    pick_candidate_location_ids,
)
from sentinel_suisse.models.enums import CountryCode, EmploymentType

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
_FACETS_FIXTURE = _FIXTURES / "richemont_facets_sample.json"
_SEARCH_FIXTURE = _FIXTURES / "richemont_search_sample.json"
_DETAIL_GENEVA_FIXTURE = _FIXTURES / "richemont_detail_geneva_sample.json"
_DETAIL_PARIS_FIXTURE = _FIXTURES / "richemont_detail_paris_sample.json"


def test_strip_html() -> None:
    raw = "<p>Who are we?</p><p>A High Jewelry Maison &amp; heritage.</p>"
    assert _strip_html(raw) == "Who are we?\nA High Jewelry Maison & heritage."
    assert _strip_html("<h2><b>Profile</b></h2><p>Student.</p>") == "Profile\nStudent."


def test_pick_employment_type() -> None:
    assert _pick_employment_type("Stage - Assistant(e) Design") == EmploymentType.INTERNSHIP
    assert _pick_employment_type("Internship 01/2027 - E-Commerce Intern") == (
        EmploymentType.INTERNSHIP
    )
    assert _pick_employment_type("CDD Remplacement 6 mois") == EmploymentType.TEMPORARY
    assert _pick_employment_type("Retail Training Senior Project Manager") == (
        EmploymentType.PERMANENT
    )


def test_pick_candidate_location_ids_filters_known_ch_fr_names() -> None:
    payload = json.loads(_FACETS_FIXTURE.read_text(encoding="utf-8"))
    settings = Settings()
    ids = pick_candidate_location_ids(payload, settings)

    # Geneva, Meyrin, Paris, and the Paris manufacture site all match known hints.
    assert set(ids) == {"loc-geneva", "loc-meyrin", "loc-paris", "loc-paris-manufacture"}
    # Dubai / New York must never be selected as CH/FR candidates.
    assert "loc-dubai" not in ids
    assert "loc-newyork" not in ids


def test_pick_candidate_location_ids_respects_extra_hints() -> None:
    payload = {
        "facets": [
            {
                "facetParameter": "locationMainGroup",
                "values": [
                    {
                        "facetParameter": "locations",
                        "values": [{"descriptor": "ZERMATT", "id": "loc-zermatt", "count": 1}],
                    }
                ],
            }
        ]
    }
    settings = Settings(richemont_extra_location_hints="Zermatt, Interlaken")
    ids = pick_candidate_location_ids(payload, settings)
    assert ids == ["loc-zermatt"]


def test_pick_candidate_location_ids_raises_on_unexpected_shape() -> None:
    with pytest.raises(RichemontFetchError, match="facets"):
        pick_candidate_location_ids({"unexpected": True}, Settings())


@patch("sentinel_suisse.ingest.connectors.richemont.httpx.get")
def test_parse_search_page_enriches_with_detail_and_filters_country(
    mock_get: MagicMock,
) -> None:
    search_payload = json.loads(_SEARCH_FIXTURE.read_text(encoding="utf-8"))
    geneva_detail = json.loads(_DETAIL_GENEVA_FIXTURE.read_text(encoding="utf-8"))
    paris_detail = json.loads(_DETAIL_PARIS_FIXTURE.read_text(encoding="utf-8"))

    def _side_effect(url: str, **_kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = geneva_detail if "GENEVA" in url else paris_detail
        return response

    mock_get.side_effect = _side_effect

    settings = Settings(ingest_rate_limit_seconds=0)
    listings = parse_search_page(search_payload, settings)

    assert len(listings) == 2
    geneva_listing = listings[0]
    assert geneva_listing.external_id == "richemont-JR129879"
    assert geneva_listing.country == CountryCode.CH
    assert geneva_listing.location == "Geneva"
    assert geneva_listing.job_category == "C231 Van Cleef & Arpels"
    assert geneva_listing.employment_type == EmploymentType.INTERNSHIP
    assert "High Jewelry Maison" in (geneva_listing.description or "")
    assert str(geneva_listing.source_url).startswith(
        "https://richemont.wd3.myworkdayjobs.com/broadbean_external/job/GENEVA/"
    )

    paris_listing = listings[1]
    assert paris_listing.country == CountryCode.FR
    assert paris_listing.location == "Paris"
    assert paris_listing.employment_type == EmploymentType.PERMANENT


@patch("sentinel_suisse.ingest.connectors.richemont.httpx.get")
def test_parse_search_page_skips_when_detail_fetch_fails(mock_get: MagicMock) -> None:
    mock_get.side_effect = httpx.ConnectError("network down")
    search_payload = json.loads(_SEARCH_FIXTURE.read_text(encoding="utf-8"))
    settings = Settings(ingest_rate_limit_seconds=0)
    listings = parse_search_page(search_payload, settings)
    assert listings == []


def test_parse_search_page_unexpected_shape_raises() -> None:
    with pytest.raises(RichemontFetchError, match="jobPostings"):
        parse_search_page({"unexpected": True}, Settings())


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_richemont_live=False)
    with pytest.raises(RichemontDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.richemont.httpx.get")
@patch("sentinel_suisse.ingest.connectors.richemont.httpx.post")
def test_fetch_search_listings_end_to_end(mock_post: MagicMock, mock_get: MagicMock) -> None:
    facets_payload = json.loads(_FACETS_FIXTURE.read_text(encoding="utf-8"))
    search_payload = json.loads(_SEARCH_FIXTURE.read_text(encoding="utf-8"))
    geneva_detail = json.loads(_DETAIL_GENEVA_FIXTURE.read_text(encoding="utf-8"))
    paris_detail = json.loads(_DETAIL_PARIS_FIXTURE.read_text(encoding="utf-8"))

    call_count = {"n": 0}

    def _post_side_effect(url: str, **kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        body = kwargs.get("json", {})
        call_count["n"] += 1
        if call_count["n"] == 1:
            # First call: the lightweight facets probe (limit=1, empty appliedFacets).
            response.json.return_value = facets_payload
        else:
            assert body.get("appliedFacets", {}).get("locations")
            response.json.return_value = search_payload
        return response

    mock_post.side_effect = _post_side_effect

    def _get_side_effect(url: str, **_kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = geneva_detail if "GENEVA" in url else paris_detail
        return response

    mock_get.side_effect = _get_side_effect

    settings = Settings(ingest_richemont_live=True, ingest_rate_limit_seconds=0)
    listings = fetch_search_listings(settings)

    assert len(listings) == 2
    assert {listing.country for listing in listings} == {CountryCode.CH, CountryCode.FR}
    # facets probe + one search page (total=2, limit=20 -> single page).
    assert mock_post.call_count == 2

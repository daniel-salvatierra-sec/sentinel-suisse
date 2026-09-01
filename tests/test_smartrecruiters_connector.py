"""SmartRecruiters connector tests (official keyless Postings API, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.smartrecruiters import (
    SmartRecruitersDisabledError,
    SmartRecruitersFetchError,
    _translate_location,
    fetch_search_listings,
    parse_postings_response,
)
from sentinel_suisse.models.enums import CountryCode, EmploymentType

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "smartrecruiters_sample.json"
_DETAIL_FIXTURE = (
    Path(__file__).resolve().parents[1] / "fixtures" / "smartrecruiters_detail_sample.json"
)


def test_translate_location() -> None:
    assert _translate_location("Genève") == "Geneva"
    assert _translate_location("Genf") == "Geneva"
    assert _translate_location("Zürich") == "Zurich"
    # Already-clean / unmapped names pass through untouched.
    assert _translate_location("Carouge") == "Carouge"


def test_parse_postings_response_from_fixture_without_details() -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    settings = Settings(smartrecruiters_fetch_details=False)
    listings = parse_postings_response(payload, settings, "HUG")

    # The Berlin/Germany posting is kept — DE/IT jobs are in the product.
    assert len(listings) == 3
    assert listings[0].external_id == "HUG-744000144240249"
    assert listings[0].country == CountryCode.CH
    # SmartRecruiters returns Swiss Romande names in French ("Genève") — the connector
    # must translate to the app's "Geneva" search convention.
    assert listings[0].location == "Geneva"
    assert listings[0].job_category == "healthcare"
    assert listings[0].employment_type == EmploymentType.PERMANENT
    assert str(listings[0].source_url) == "https://jobs.smartrecruiters.com/HUG/744000144240249"
    assert listings[0].description is None
    assert listings[1].employment_type == EmploymentType.INTERNSHIP
    assert listings[2].country == CountryCode.DE
    assert listings[2].location == "Berlin"


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_smartrecruiters_live=False)
    with pytest.raises(SmartRecruitersDisabledError):
        fetch_search_listings(settings)


def test_fetch_raises_when_companies_empty() -> None:
    settings = Settings(ingest_smartrecruiters_live=True, smartrecruiters_companies="")
    with pytest.raises(SmartRecruitersFetchError, match="SMARTRECRUITERS_COMPANIES"):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.smartrecruiters.httpx.get")
def test_fetch_search_listings_enriches_with_detail(mock_get: MagicMock) -> None:
    postings_payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    detail_payload = json.loads(_DETAIL_FIXTURE.read_text(encoding="utf-8"))

    def _side_effect(url: str, **kwargs: object) -> MagicMock:
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        if "/postings/" in url and url.rstrip("/").split("/")[-1] != "postings":
            response.json.return_value = detail_payload
            return response
        params = kwargs.get("params") if isinstance(kwargs.get("params"), dict) else {}
        if params.get("country") not in (None, "ch"):
            response.json.return_value = {"content": [], "totalFound": 0, "offset": 0, "limit": 100}
            return response
        response.json.return_value = postings_payload
        return response

    mock_get.side_effect = _side_effect

    settings = Settings(
        ingest_smartrecruiters_live=True,
        smartrecruiters_companies="HUG",
        smartrecruiters_fetch_details=True,
        ingest_rate_limit_seconds=0,
    )
    listings = fetch_search_listings(settings)

    assert len(listings) == 3
    first = listings[0]
    assert first.description is not None
    assert "soins palliatifs" in first.description
    assert str(first.source_url).startswith("https://jobs.smartrecruiters.com/HUG/744000144240249-")


@patch("sentinel_suisse.ingest.connectors.smartrecruiters.httpx.get")
def test_fetch_search_listings_multiple_companies(mock_get: MagicMock) -> None:
    postings_payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    empty = {"content": [], "totalFound": 0, "offset": 0, "limit": 100}

    def _side_effect(_url: str, **kwargs: object) -> MagicMock:
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        params = kwargs.get("params") if isinstance(kwargs.get("params"), dict) else {}
        if params.get("country") not in (None, "ch"):
            response.json.return_value = empty
        else:
            response.json.return_value = postings_payload
        return response

    mock_get.side_effect = _side_effect

    settings = Settings(
        ingest_smartrecruiters_live=True,
        smartrecruiters_companies="HUG, SGS",
        smartrecruiters_fetch_details=False,
        ingest_rate_limit_seconds=0,
    )
    listings = fetch_search_listings(settings)

    # 3 valid postings per company x 2 companies (CH slice only in this mock).
    assert len(listings) == 6


@patch("sentinel_suisse.ingest.connectors.smartrecruiters.httpx.get")
def test_fetch_skips_unknown_company(mock_get: MagicMock) -> None:
    request = httpx.Request("GET", "https://api.smartrecruiters.com/v1/companies/Nope/postings")
    mock_get.return_value = httpx.Response(404, request=request)

    settings = Settings(
        ingest_smartrecruiters_live=True,
        smartrecruiters_companies="Nope",
        smartrecruiters_fetch_details=False,
        ingest_rate_limit_seconds=0,
    )
    assert fetch_search_listings(settings) == []


def test_fetch_search_listings_unexpected_shape_raises() -> None:
    settings = Settings(
        ingest_smartrecruiters_live=True,
        smartrecruiters_companies="HUG",
        ingest_rate_limit_seconds=0,
    )
    with pytest.raises(SmartRecruitersFetchError, match="content"):
        parse_postings_response({"unexpected": True}, settings, "HUG")

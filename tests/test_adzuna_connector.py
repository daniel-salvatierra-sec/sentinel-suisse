"""Adzuna connector tests (official job aggregator API, no live network)."""

import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna import (
    AdzunaDisabledError,
    AdzunaFetchError,
    fetch_search_listings,
    parse_search_response,
)
from sentinel_suisse.models.enums import CountryCode, EmploymentType

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "adzuna_sample.json"


def test_parse_search_response_from_fixture() -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    listings = parse_search_response(payload, CountryCode.CH)
    assert len(listings) == 2
    assert listings[0].external_id == "4812345678"
    assert listings[0].country == CountryCode.CH
    assert listings[0].location == "Genève"
    assert listings[0].job_category == "IT Jobs"
    assert listings[0].employment_type == EmploymentType.PERMANENT
    assert listings[0].price == Decimal("90000")
    assert str(listings[0].source_url).startswith("https://www.adzuna.ch/")
    assert listings[1].employment_type == EmploymentType.TEMPORARY
    assert listings[1].price is None


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_adzuna_live=False)
    with pytest.raises(AdzunaDisabledError):
        fetch_search_listings(settings)


def test_fetch_raises_when_credentials_missing() -> None:
    settings = Settings(ingest_adzuna_live=True, adzuna_app_id="", adzuna_app_key="")
    with pytest.raises(AdzunaFetchError, match="developer.adzuna.com"):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.adzuna.httpx.get")
def test_fetch_search_listings_when_enabled(mock_get: MagicMock) -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = payload
    mock_get.return_value = response

    settings = Settings(
        ingest_adzuna_live=True,
        adzuna_app_id="test-app-id",
        adzuna_app_key="test-app-key",  # noqa: S106
        adzuna_country="ch",
        adzuna_location="Geneve",
        ingest_rate_limit_seconds=0,
    )
    listings = fetch_search_listings(settings)

    assert len(listings) == 2
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args.args[0] == "https://api.adzuna.com/v1/api/jobs/ch/search/1"
    call_params = call_args.kwargs["params"]
    assert call_params["app_id"] == "test-app-id"
    assert call_params["where"] == "Geneve"


@patch("sentinel_suisse.ingest.connectors.adzuna.httpx.get")
def test_fetch_search_listings_unexpected_shape_raises(mock_get: MagicMock) -> None:
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {"unexpected": True}
    mock_get.return_value = response

    settings = Settings(
        ingest_adzuna_live=True,
        adzuna_app_id="test-app-id",
        adzuna_app_key="test-app-key",  # noqa: S106
        ingest_rate_limit_seconds=0,
    )
    with pytest.raises(AdzunaFetchError, match="results"):
        fetch_search_listings(settings)

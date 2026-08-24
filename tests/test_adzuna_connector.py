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
    _translate_location,
    fetch_search_listings,
    parse_search_response,
)
from sentinel_suisse.models.enums import CountryCode, EmploymentType

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "adzuna_sample.json"


def test_translate_location_drops_german_scaffolding() -> None:
    # Canton-only (no specific city known) -> just the translated canton name.
    assert _translate_location("Kanton Genf, Schweiz") == "Geneva"
    # City-level -> keep the city, translate the canton, no leftover German words.
    assert _translate_location("Thônex, Genf") == "Thônex, Geneva"
    assert _translate_location("Carouge, Genf") == "Carouge, Geneva"
    assert _translate_location("Lausanne, Waadt") == "Lausanne, Vaud"
    # Already-clean names pass through untouched.
    assert _translate_location("Chêne-Bougeries, Geneva") == "Chêne-Bougeries, Geneva"


def test_parse_search_response_from_fixture() -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    listings = parse_search_response(payload, CountryCode.CH)
    assert len(listings) == 2
    assert listings[0].external_id == "4812345678"
    assert listings[0].country == CountryCode.CH
    # Adzuna returns Swiss location names in German ("Kanton Genf, Schweiz") — the
    # connector must translate them to match the app's "Geneva" search convention,
    # without leaving German scaffolding words ("Kanton", "Schweiz") mixed in.
    assert listings[0].location == "Geneva"
    assert listings[0].job_category == "software"
    assert listings[0].employment_type == EmploymentType.PERMANENT
    assert listings[0].price == Decimal("90000")
    assert str(listings[0].source_url).startswith("https://www.adzuna.ch/")
    assert listings[1].location == "Lausanne, Vaud"
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
        adzuna_locations="",
        adzuna_role_keywords="",
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
def test_fetch_walks_swiss_cities(mock_get: MagicMock) -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = payload
    mock_get.return_value = response

    listings = fetch_search_listings(
        Settings(
            ingest_adzuna_live=True,
            adzuna_app_id="test-app-id",
            adzuna_app_key="test-app-key",  # noqa: S106
            adzuna_country="ch",
            adzuna_locations="Geneve,Zurich,Bern",
            adzuna_role_keywords="",
            ingest_rate_limit_seconds=0,
        )
    )

    assert len(listings) == 2
    assert mock_get.call_count == 3
    wheres = [call.kwargs["params"]["where"] for call in mock_get.call_args_list]
    assert wheres == ["Geneve", "Zurich", "Bern"]


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


@patch("sentinel_suisse.ingest.connectors.adzuna.httpx.get")
def test_fetch_role_keywords_query_hub_cities(mock_get: MagicMock) -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = payload
    mock_get.return_value = response

    fetch_search_listings(
        Settings(
            ingest_adzuna_live=True,
            adzuna_app_id="test-app-id",
            adzuna_app_key="test-app-key",  # noqa: S106
            adzuna_country="ch",
            adzuna_locations="Geneve",
            adzuna_role_keywords="chauffeur,taxi",
            adzuna_role_locations="Geneve,Basel",
            adzuna_role_max_pages=1,
            ingest_rate_limit_seconds=0,
        )
    )

    whats = [call.kwargs["params"].get("what") for call in mock_get.call_args_list]
    assert whats.count("chauffeur") == 2
    assert whats.count("taxi") == 2

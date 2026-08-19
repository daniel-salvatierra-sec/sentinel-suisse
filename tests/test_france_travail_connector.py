"""France Travail connector tests (OAuth2 + REST, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.france_travail import (
    FranceTravailDisabledError,
    FranceTravailFetchError,
    fetch_search_listings,
    parse_search_response,
)
from sentinel_suisse.models.enums import CountryCode, EmploymentType

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "france_travail_sample.json"


def test_parse_search_response_from_fixture() -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    listings = parse_search_response(payload)
    assert len(listings) == 2
    assert listings[0].external_id == "048KLTP"
    assert listings[0].country == CountryCode.FR
    assert listings[0].location == "74 - ANNEMASSE"
    assert listings[0].job_category == "Développement informatique"
    assert listings[0].employment_type == EmploymentType.PERMANENT
    assert str(listings[0].source_url).startswith("https://candidat.francetravail.fr/")
    assert listings[1].employment_type == EmploymentType.TEMPORARY
    # No urlOrigine on the second offer — falls back to the candidate detail page.
    assert "049ABCD" in str(listings[1].source_url)


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_france_travail_live=False)
    with pytest.raises(FranceTravailDisabledError):
        fetch_search_listings(settings)


def test_fetch_raises_when_credentials_missing() -> None:
    settings = Settings(
        ingest_france_travail_live=True,
        france_travail_client_id="",
        france_travail_client_secret="",
    )
    with pytest.raises(FranceTravailFetchError, match="francetravail.io"):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.france_travail.httpx.get")
@patch("sentinel_suisse.ingest.connectors.france_travail.httpx.post")
def test_fetch_search_listings_when_enabled(mock_post: MagicMock, mock_get: MagicMock) -> None:
    token_response = MagicMock()
    token_response.raise_for_status = MagicMock()
    token_response.json.return_value = {"access_token": "fake-token", "expires_in": 1500}
    mock_post.return_value = token_response

    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    search_response = MagicMock()
    search_response.status_code = 200
    search_response.json.return_value = payload
    mock_get.return_value = search_response

    settings = Settings(
        ingest_france_travail_live=True,
        france_travail_client_id="test-client",
        france_travail_client_secret="test-secret",  # noqa: S106
        ingest_rate_limit_seconds=0,
    )
    listings = fetch_search_listings(settings)

    assert len(listings) == 2
    mock_post.assert_called_once()
    mock_get.assert_called_once()
    call_headers = mock_get.call_args.kwargs["headers"]
    assert call_headers["Authorization"] == "Bearer fake-token"
    call_params = mock_get.call_args.kwargs["params"]
    assert call_params["departement"] == "74"


@patch("sentinel_suisse.ingest.connectors.france_travail.httpx.get")
@patch("sentinel_suisse.ingest.connectors.france_travail.httpx.post")
def test_fetch_search_listings_returns_empty_on_204(
    mock_post: MagicMock, mock_get: MagicMock
) -> None:
    token_response = MagicMock()
    token_response.raise_for_status = MagicMock()
    token_response.json.return_value = {"access_token": "fake-token"}
    mock_post.return_value = token_response

    search_response = MagicMock()
    search_response.status_code = 204
    mock_get.return_value = search_response

    settings = Settings(
        ingest_france_travail_live=True,
        france_travail_client_id="test-client",
        france_travail_client_secret="test-secret",  # noqa: S106
        ingest_rate_limit_seconds=0,
    )
    listings = fetch_search_listings(settings)
    assert listings == []

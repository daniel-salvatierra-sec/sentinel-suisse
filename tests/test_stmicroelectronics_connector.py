"""STMicroelectronics connector tests (Eightfold JSON API, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.stmicroelectronics import (
    STMicroelectronicsDisabledError,
    STMicroelectronicsFetchError,
    fetch_search_listings,
    parse_list_page,
    pick_country,
)
from sentinel_suisse.models.enums import CountryCode

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
_LIST_FIXTURE = _FIXTURES / "stmicroelectronics_list_sample.json"
_DETAIL_GENEVA = _FIXTURES / "stmicroelectronics_detail_geneva_sample.json"
_DETAIL_FRANCE = _FIXTURES / "stmicroelectronics_detail_france_sample.json"


def test_pick_country() -> None:
    assert pick_country("Geneva, Switzerland") == CountryCode.CH
    assert pick_country("Plan-les-Ouates, Suisse") == CountryCode.CH
    assert pick_country("Grenoble, France") == CountryCode.FR
    assert pick_country("Greater Noida, India") is None
    assert pick_country(None) is None


def test_fetch_raises_when_live_disabled() -> None:
    with pytest.raises(STMicroelectronicsDisabledError):
        fetch_search_listings(Settings(ingest_stmicroelectronics_live=False))


def test_parse_list_page_unexpected_shape() -> None:
    with pytest.raises(STMicroelectronicsFetchError, match="positions"):
        parse_list_page({"unexpected": True}, Settings())


@patch("sentinel_suisse.ingest.connectors.stmicroelectronics.httpx.get")
def test_parse_list_page_filters_country_and_enriches(mock_get: MagicMock) -> None:
    geneva = json.loads(_DETAIL_GENEVA.read_text(encoding="utf-8"))
    france = json.loads(_DETAIL_FRANCE.read_text(encoding="utf-8"))

    def _side_effect(url: str, **_kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = geneva if "563637172000001" in url else france
        return response

    mock_get.side_effect = _side_effect
    payload = json.loads(_LIST_FIXTURE.read_text(encoding="utf-8"))
    listings = parse_list_page(payload, Settings(ingest_rate_limit_seconds=0))

    assert len(listings) == 2
    assert listings[0].external_id == "stmicroelectronics-563637172000001"
    assert listings[0].country == CountryCode.CH
    assert listings[0].location == "Geneva"
    assert "legal team" in (listings[0].description or "").lower()
    assert listings[1].country == CountryCode.FR
    assert listings[1].location == "Grenoble"
    assert mock_get.call_count == 2


@patch("sentinel_suisse.ingest.connectors.stmicroelectronics.httpx.get")
def test_parse_skips_when_detail_fails(mock_get: MagicMock) -> None:
    mock_get.side_effect = httpx.ConnectError("down")
    payload = {
        "positions": [
            {"id": 1, "name": "Intern", "location": "Geneva, Switzerland"},
        ]
    }
    listings = parse_list_page(payload, Settings(ingest_rate_limit_seconds=0))
    assert len(listings) == 1
    assert listings[0].description is None


@patch("sentinel_suisse.ingest.connectors.stmicroelectronics.httpx.get")
def test_fetch_paginates(mock_get: MagicMock) -> None:
    list_payload = json.loads(_LIST_FIXTURE.read_text(encoding="utf-8"))
    geneva = json.loads(_DETAIL_GENEVA.read_text(encoding="utf-8"))
    france = json.loads(_DETAIL_FRANCE.read_text(encoding="utf-8"))

    def _side_effect(url: str, **_kwargs: object) -> MagicMock:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        last = url.rstrip("/").split("/")[-1]
        if last.isdigit():
            response.json.return_value = geneva if last == "563637172000001" else france
        else:
            response.json.return_value = list_payload
        return response

    mock_get.side_effect = _side_effect
    listings = fetch_search_listings(
        Settings(ingest_stmicroelectronics_live=True, ingest_rate_limit_seconds=0)
    )
    assert len(listings) == 2
    assert {item.country for item in listings} == {CountryCode.CH, CountryCode.FR}

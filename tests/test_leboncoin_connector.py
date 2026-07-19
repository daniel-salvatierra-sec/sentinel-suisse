"""Leboncoin connector parser tests (no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.leboncoin import (
    LeboncoinDisabledError,
    fetch_search_listings,
    parse_search_state,
)
from sentinel_suisse.models.enums import CountryCode, PropertyType

_FIXTURE_STATE = Path(__file__).resolve().parents[1] / "fixtures" / "leboncoin_initial_state.json"


def test_parse_search_state_from_fixture() -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    listings = parse_search_state(state)
    assert len(listings) == 2
    assert listings[0].external_id == "2500111222"
    assert listings[0].country == CountryCode.FR
    assert listings[0].location == "Annemasse, 74100"
    assert listings[0].rooms is not None
    assert listings[0].has_parking is True
    assert listings[1].property_type == PropertyType.STUDIO


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_leboncoin_live=False)
    with pytest.raises(LeboncoinDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.leboncoin.httpx.get")
def test_fetch_search_listings_when_enabled(mock_get: MagicMock) -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    html = f"<html><script>window.__NEXT_DATA__={json.dumps(state)};</script></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    settings = Settings(ingest_leboncoin_live=True, ingest_rate_limit_seconds=0)
    listings = fetch_search_listings(settings)
    assert len(listings) == 2
    mock_get.assert_called_once()

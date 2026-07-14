"""Flatfox connector parser tests (no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.flatfox import (
    FlatfoxDisabledError,
    fetch_search_listings,
    parse_search_state,
)

_FIXTURE_STATE = Path(__file__).resolve().parents[1] / "fixtures" / "flatfox_initial_state.json"


def test_parse_search_state_from_fixture() -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    listings = parse_search_state(state)
    assert len(listings) == 2
    assert listings[0].external_id == "800111222"
    assert listings[0].title.startswith("Appartement")
    assert listings[0].location == "Genève, 1201"
    assert str(listings[0].source_url) == "https://flatfox.ch/en/flat/800111222/"
    assert listings[1].location == "Carouge, 1227"


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_flatfox_live=False)
    with pytest.raises(FlatfoxDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.flatfox.httpx.get")
def test_fetch_search_listings_when_enabled(mock_get: MagicMock) -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    html = f"<html><script>window.__INITIAL_STATE__={json.dumps(state)};</script></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    settings = Settings(ingest_flatfox_live=True, ingest_rate_limit_seconds=0)
    listings = fetch_search_listings(settings)
    assert len(listings) == 2
    mock_get.assert_called_once()

"""ImmoScout24 connector parser tests (no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.immoscout import (
    ImmoscoutDisabledError,
    fetch_search_listings,
    parse_search_state,
)

_FIXTURE_STATE = Path(__file__).resolve().parents[1] / "fixtures" / "immoscout_initial_state.json"


def test_parse_search_state_from_fixture() -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    listings = parse_search_state(state)
    assert len(listings) == 2
    assert listings[0].external_id == "400555666"
    assert listings[0].title.startswith("Appartement")
    assert listings[0].location == "Genève, 1204"
    assert str(listings[0].source_url) == "https://www.immoscout24.ch/fr/d/400555666"
    assert listings[1].location == "Vernier, 1214"
    assert listings[0].price is not None
    assert str(listings[0].price) == "2100"


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_immoscout_live=False)
    with pytest.raises(ImmoscoutDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.immoscout.httpx.get")
def test_fetch_search_listings_when_enabled(mock_get: MagicMock) -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    html = f"<html><script>window.__INITIAL_STATE__={json.dumps(state)};</script></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    settings = Settings(ingest_immoscout_live=True, ingest_rate_limit_seconds=0)
    listings = fetch_search_listings(settings)
    assert len(listings) == 2
    mock_get.assert_called_once()

"""Indeed FR connector parser tests (no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.indeed_fr import (
    IndeedFrDisabledError,
    fetch_search_listings,
    parse_search_state,
)
from sentinel_suisse.models.enums import CountryCode, EmploymentType

_FIXTURE_STATE = Path(__file__).resolve().parents[1] / "fixtures" / "indeed_fr_initial_state.json"


def test_parse_search_state_from_fixture() -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    listings = parse_search_state(state)
    assert len(listings) == 2
    assert listings[0].external_id == "abc111fr"
    assert listings[0].country == CountryCode.FR
    assert listings[0].location == "Annemasse (74)"
    assert listings[0].job_category == "it"
    assert listings[0].employment_type == EmploymentType.PERMANENT
    assert listings[1].employment_type == EmploymentType.TEMPORARY


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_indeed_fr_live=False)
    with pytest.raises(IndeedFrDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.indeed_fr.httpx.get")
def test_fetch_search_listings_when_enabled(mock_get: MagicMock) -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    html = f"<html><script>window.__NEXT_DATA__={json.dumps(state)};</script></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    settings = Settings(ingest_indeed_fr_live=True, ingest_rate_limit_seconds=0)
    listings = fetch_search_listings(settings)
    assert len(listings) == 2
    mock_get.assert_called_once()

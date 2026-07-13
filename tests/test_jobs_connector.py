"""jobs.ch connector parser tests (no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.jobs import (
    JobsDisabledError,
    fetch_search_listings,
    parse_search_state,
)
from sentinel_suisse.models.enums import ListingType

_FIXTURE_STATE = Path(__file__).resolve().parents[1] / "fixtures" / "jobs_initial_state.json"


def test_parse_jobs_state_from_fixture() -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    listings = parse_search_state(state)
    assert len(listings) == 2
    assert listings[0].listing_type == ListingType.JOB
    assert listings[0].external_id == "7d5597bc-9ec1-412a-9a81-33afacd9bb1c"
    assert listings[0].title.startswith("Software Engineer")
    assert listings[0].location == "Geneva"
    assert listings[0].price is None
    assert str(listings[0].source_url).startswith("https://www.jobs.ch/")


def test_fetch_raises_when_live_disabled() -> None:
    settings = Settings(ingest_jobs_live=False)
    with pytest.raises(JobsDisabledError):
        fetch_search_listings(settings)


@patch("sentinel_suisse.ingest.connectors.jobs.httpx.get")
def test_fetch_jobs_listings_when_enabled(mock_get: MagicMock) -> None:
    state = json.loads(_FIXTURE_STATE.read_text(encoding="utf-8"))
    html = f"<html><script>window.__NEXT_DATA__={json.dumps(state)};</script></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    settings = Settings(ingest_jobs_live=True, ingest_rate_limit_seconds=0)
    listings = fetch_search_listings(settings)
    assert len(listings) == 2
    mock_get.assert_called_once()

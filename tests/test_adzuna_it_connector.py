"""Adzuna Italy border connector (official API, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna_it import (
    AdzunaItDisabledError,
    fetch_search_listings,
)
from sentinel_suisse.models.enums import CountryCode

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "adzuna_sample.json"


def test_fetch_raises_when_live_disabled() -> None:
    with pytest.raises(AdzunaItDisabledError):
        fetch_search_listings(Settings(ingest_adzuna_it_live=False))


@patch("sentinel_suisse.ingest.connectors.adzuna.httpx.get")
def test_fetch_uses_italy_endpoint_and_location(mock_get: MagicMock) -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = payload
    mock_get.return_value = response

    listings = fetch_search_listings(
        Settings(
            ingest_adzuna_it_live=True,
            adzuna_app_id="test-app-id",
            adzuna_app_key="test-app-key",  # noqa: S106
            adzuna_it_location="Como",
            ingest_rate_limit_seconds=0,
        )
    )

    assert listings[0].country == CountryCode.IT
    urls = [call.args[0] for call in mock_get.call_args_list]
    assert any(url.endswith("/jobs/it/search/1") for url in urls)
    wheres = [call.kwargs["params"]["where"] for call in mock_get.call_args_list]
    assert "Como" in wheres
    assert "Varese" in wheres

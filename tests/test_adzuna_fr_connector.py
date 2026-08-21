"""Adzuna France connector tests (official API, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna_fr import (
    AdzunaFrDisabledError,
    fetch_search_listings,
)
from sentinel_suisse.models.enums import CountryCode

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "adzuna_sample.json"


def test_fetch_raises_when_live_disabled() -> None:
    with pytest.raises(AdzunaFrDisabledError):
        fetch_search_listings(Settings(ingest_adzuna_fr_live=False))


@patch("sentinel_suisse.ingest.connectors.adzuna.httpx.get")
def test_fetch_uses_france_endpoint_and_location(mock_get: MagicMock) -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = payload
    mock_get.return_value = response

    listings = fetch_search_listings(
        Settings(
            ingest_adzuna_fr_live=True,
            adzuna_app_id="test-app-id",
            adzuna_app_key="test-app-key",  # noqa: S106
            adzuna_fr_location="Annemasse",
            ingest_rate_limit_seconds=0,
        )
    )

    assert len(listings) == 2
    assert listings[0].country == CountryCode.FR
    mock_get.assert_called_once()
    assert mock_get.call_args.args[0] == "https://api.adzuna.com/v1/api/jobs/fr/search/1"
    assert mock_get.call_args.kwargs["params"]["where"] == "Annemasse"

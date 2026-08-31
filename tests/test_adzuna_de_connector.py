"""Adzuna Germany border connector (official API, no live network)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.adzuna_de import (
    AdzunaDeDisabledError,
    fetch_search_listings,
)
from sentinel_suisse.models.enums import CountryCode

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "adzuna_sample.json"


def test_fetch_raises_when_live_disabled() -> None:
    with pytest.raises(AdzunaDeDisabledError):
        fetch_search_listings(Settings(ingest_adzuna_de_live=False))


@patch("sentinel_suisse.ingest.connectors.adzuna.httpx.get")
def test_fetch_uses_germany_endpoint_and_location(mock_get: MagicMock) -> None:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = payload
    mock_get.return_value = response

    listings = fetch_search_listings(
        Settings(
            ingest_adzuna_de_live=True,
            adzuna_app_id="test-app-id",
            adzuna_app_key="test-app-key",  # noqa: S106
            adzuna_de_location="Konstanz",
            ingest_rate_limit_seconds=0,
        )
    )

    assert listings[0].country == CountryCode.DE
    urls = [call.args[0] for call in mock_get.call_args_list]
    assert any(url.endswith("/jobs/de/search/1") for url in urls)
    wheres = [call.kwargs["params"]["where"] for call in mock_get.call_args_list]
    assert "Konstanz" in wheres
    assert "Lorrach" in wheres
    assert "Berlin" in wheres

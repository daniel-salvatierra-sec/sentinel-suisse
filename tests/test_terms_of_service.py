"""Tests for published terms of service API."""

import pytest
from fastapi.testclient import TestClient

ALL_LANGUAGES = ("fr", "de", "es", "pt", "en")

CONTENT_MARKERS = {
    "fr": "nLPD",
    "de": "nDSG",
    "es": "nLPD",
    "pt": "nLPD",
    "en": "nFADP",
}


@pytest.mark.parametrize("lang", ALL_LANGUAGES)
def test_terms_of_service_all_languages(client: TestClient, lang: str) -> None:
    response = client.get(f"/api/v1/legal/terms?lang={lang}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["lang"] == lang
    assert data["version"] == "2026-07-16"
    assert CONTENT_MARKERS[lang] in data["content"]
    assert data["privacy_endpoint"] == "/api/v1/legal/privacy"
    assert set(data["supported_languages"]) == set(ALL_LANGUAGES)


def test_terms_default_language_is_french(client: TestClient) -> None:
    response = client.get("/api/v1/legal/terms")
    assert response.status_code == 200
    assert response.json()["lang"] == "fr"


def test_terms_rejects_invalid_language(client: TestClient) -> None:
    response = client.get("/api/v1/legal/terms?lang=it")
    assert response.status_code == 422

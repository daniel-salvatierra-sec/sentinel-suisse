"""Tests for published privacy policy API."""

from fastapi.testclient import TestClient


def test_privacy_policy_french(client: TestClient) -> None:
    response = client.get("/api/v1/legal/privacy?lang=fr")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["lang"] == "fr"
    assert data["version"] == "2026-07-13"
    assert "nLPD" in data["content"]
    assert data["erasure_endpoint"] == "/api/v1/users/me"


def test_privacy_policy_german(client: TestClient) -> None:
    response = client.get("/api/v1/legal/privacy?lang=de")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["lang"] == "de"
    assert "nDSG" in data["content"] or "nLPD" in data["content"]


def test_privacy_policy_default_language_is_french(client: TestClient) -> None:
    response = client.get("/api/v1/legal/privacy")
    assert response.status_code == 200
    assert response.json()["lang"] == "fr"


def test_privacy_policy_rejects_invalid_language(client: TestClient) -> None:
    response = client.get("/api/v1/legal/privacy?lang=en")
    assert response.status_code == 422

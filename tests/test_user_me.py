"""Tests for GET /api/v1/users/me."""

import uuid

from fastapi.testclient import TestClient


def _unique_email() -> str:
    return f"me-{uuid.uuid4().hex[:10]}@example.com"


def _create_user(client: TestClient, admin_auth: tuple[str, str]) -> tuple[str, str]:
    email = _unique_email()
    response = client.post(
        "/api/v1/users",
        json={"email": email, "is_active": True, "locale": "fr"},
        auth=admin_auth,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    return data["api_key"], email


def test_get_me_returns_profile(client: TestClient, admin_auth: tuple[str, str]) -> None:
    api_key, email = _create_user(client, admin_auth)
    response = client.get("/api/v1/users/me", headers={"X-API-Key": api_key})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == email
    assert data["locale"] == "fr"
    assert data["is_active"] is True
    assert data.get("accept_profile") is None


def test_get_me_requires_api_key(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_patch_me_accept_profile(client: TestClient, admin_auth: tuple[str, str]) -> None:
    api_key, _email = _create_user(client, admin_auth)
    headers = {"X-API-Key": api_key}
    response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={
            "accept_profile": {
                "goal": "both",
                "live_in": "Annemasse",
                "work_in": "Genève",
                "permit": "G",
                "languages": "ES B2, FR A2",
                "budget_chf": 1800,
                "cities": "Genève, Annemasse",
                "household": 2,
            }
        },
    )
    assert response.status_code == 200, response.text
    profile = response.json()["accept_profile"]
    assert profile["goal"] == "both"
    assert profile["permit"] == "G"
    assert profile["budget_chf"] == 1800
    assert profile["live_in"] == "Annemasse"

    cleared = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"accept_profile": {}},
    )
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["accept_profile"] is None

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


def test_get_me_requires_api_key(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

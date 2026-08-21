"""Landlord-posted housing ads."""

import uuid

from fastapi.testclient import TestClient


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _create_user(client: TestClient, admin_auth: tuple[str, str]) -> str:
    response = client.post(
        "/api/v1/users",
        json={"email": _email("direct"), "is_active": True},
        auth=admin_auth,
    )
    assert response.status_code == 201, response.text
    return response.json()["api_key"]


def _payload() -> dict:
    return {
        "title": "3.5 pieces Plainpalais",
        "location": "Geneva, 1205",
        "price": 2100,
        "rooms": 3.5,
        "has_parking": True,
        "contact_url": "https://example.com/flat",
        "description": "Sunny apartment near tram.",
    }


def test_user_can_post_and_delete_housing(client: TestClient, admin_auth: tuple[str, str]) -> None:
    key = _create_user(client, admin_auth)
    created = client.post(
        "/api/v1/me/listings",
        headers={"X-API-Key": key},
        json=_payload(),
    )
    assert created.status_code == 201, created.text
    listing_id = created.json()["id"]
    assert created.json()["listing_type"] == "housing"
    assert created.json()["location"] == "Geneva, 1205"

    listed = client.get("/api/v1/me/listings", headers={"X-API-Key": key})
    assert listed.status_code == 200
    assert any(item["id"] == listing_id for item in listed.json())

    deleted = client.delete(f"/api/v1/me/listings/{listing_id}", headers={"X-API-Key": key})
    assert deleted.status_code == 204


def test_user_cannot_delete_someone_elses_listing(
    client: TestClient, admin_auth: tuple[str, str]
) -> None:
    key_a = _create_user(client, admin_auth)
    key_b = _create_user(client, admin_auth)
    created = client.post(
        "/api/v1/me/listings",
        headers={"X-API-Key": key_a},
        json=_payload(),
    )
    assert created.status_code == 201, created.text
    listing_id = created.json()["id"]
    denied = client.delete(f"/api/v1/me/listings/{listing_id}", headers={"X-API-Key": key_b})
    assert denied.status_code == 404

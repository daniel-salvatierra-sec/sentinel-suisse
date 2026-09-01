"""Landlord-posted housing ads."""

import uuid

from fastapi.testclient import TestClient

from sentinel_suisse.models.enums import CountryCode
from sentinel_suisse.schemas.direct_listing import DirectListingCreate


def test_schema_accepts_france_border_housing() -> None:
    payload = DirectListingCreate(
        title="T3 centre Annemasse parking",
        location="Annemasse",
        country=CountryCode.FR,
        price=980,
        rooms=3,
        contact_url="+33 6 12 34 56 78",
    )
    assert payload.country == CountryCode.FR
    assert payload.contact_url == "https://wa.me/33612345678"


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
    assert created.json()["country"] == "CH"

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


def test_user_can_post_a_job(client: TestClient, admin_auth: tuple[str, str]) -> None:
    key = _create_user(client, admin_auth)
    created = client.post(
        "/api/v1/me/listings",
        headers={"X-API-Key": key},
        json={
            "listing_type": "job",
            "title": "Infirmier HUG temps partiel",
            "location": "Geneva",
            "job_category": "healthcare",
            "contact_url": "https://example.com/apply",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["listing_type"] == "job"
    assert created.json()["job_category"] == "healthcare"


def test_user_can_post_a_job_with_phone(client: TestClient, admin_auth: tuple[str, str]) -> None:
    key = _create_user(client, admin_auth)
    created = client.post(
        "/api/v1/me/listings",
        headers={"X-API-Key": key},
        json={
            "listing_type": "job",
            "title": "Chofer de bus Geneva",
            "location": "Geneva",
            "job_category": "logistics",
            "contact_url": "079 123 45 67",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["source_url"] == "https://wa.me/41791234567"


def test_user_can_post_housing_in_france_border(
    client: TestClient, admin_auth: tuple[str, str]
) -> None:
    key = _create_user(client, admin_auth)
    created = client.post(
        "/api/v1/me/listings",
        headers={"X-API-Key": key},
        json={
            "title": "T3 centre Annemasse parking",
            "location": "Annemasse",
            "country": "FR",
            "price": 980,
            "rooms": 3,
            "contact_url": "+33 6 12 34 56 78",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["country"] == "FR"
    assert created.json()["location"] == "Annemasse"

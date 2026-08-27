"""Public city picker stock endpoint."""

import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.api.auth import verify_admin


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def operator_client(client: TestClient) -> TestClient:
    client.app.dependency_overrides[verify_admin] = lambda: "admin"
    yield client
    client.app.dependency_overrides.pop(verify_admin, None)


def test_public_cities_lists_only_stocked(operator_client: TestClient) -> None:
    empty = operator_client.get("/api/v1/public/cities")
    assert empty.status_code == 200, empty.text
    assert isinstance(empty.json(), list)

    user = operator_client.post(
        "/api/v1/users",
        json={"email": _email("city-stock"), "is_active": True},
    )
    assert user.status_code == 201, user.text
    api_key = user.json()["api_key"]

    title = f"City-stock-{uuid.uuid4().hex[:8]}"
    created = operator_client.post(
        "/api/v1/me/listings",
        headers={"X-API-Key": api_key},
        json={
            "title": title,
            "location": "Fribourg",
            "price": 1600,
            "contact_url": "https://example.com/city-stock",
        },
    )
    assert created.status_code == 201, created.text

    after = operator_client.get("/api/v1/public/cities")
    assert after.status_code == 200, after.text
    cities = {row["city"]: row for row in after.json()}
    assert "Fribourg" in cities
    assert cities["Fribourg"]["total"] >= 1
    assert cities["Fribourg"]["housing_count"] >= 1
    assert all(row["total"] > 0 for row in after.json())

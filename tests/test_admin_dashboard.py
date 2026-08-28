"""Owner dashboard API and production /docs gate."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.api.auth import verify_admin
from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app


@pytest.fixture
def operator_client(client: TestClient) -> TestClient:
    client.app.dependency_overrides[verify_admin] = lambda: "admin"
    yield client
    client.app.dependency_overrides.pop(verify_admin, None)


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def test_docs_disabled_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("TRUSTED_HOSTS", "")
    get_settings.cache_clear()
    client = TestClient(create_app())
    try:
        response = client.get("/docs")
        assert response.status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404
    finally:
        monkeypatch.setenv("APP_ENV", os.environ.get("APP_ENV", "development"))
        get_settings.cache_clear()


def test_docs_available_in_development(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200


def test_admin_overview_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/admin/overview")
    assert response.status_code in {401, 503}


def test_admin_overview_and_premium_toggle(operator_client: TestClient) -> None:
    created = operator_client.post(
        "/api/v1/users",
        json={"email": _email("dash"), "is_active": True},
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]

    overview = operator_client.get("/api/v1/admin/overview")
    assert overview.status_code == 200, overview.text
    data = overview.json()
    assert data["users_total"] >= 1
    assert data["users_premium"] >= 0
    assert "listings_housing" in data
    assert "listings_job" in data
    assert "listings_direct" in data
    assert "listings_hidden" in data
    assert data["database_ok"] is True
    assert isinstance(data["providers"], list)

    users = operator_client.get("/api/v1/admin/users?limit=50")
    assert users.status_code == 200, users.text
    assert any(item["id"] == user_id for item in users.json())

    premium = operator_client.patch(
        f"/api/v1/admin/users/{user_id}/premium",
        json={"is_premium": True},
    )
    assert premium.status_code == 200, premium.text
    assert premium.json()["is_premium"] is True

    erased = operator_client.delete(f"/api/v1/admin/users/{user_id}")
    assert erased.status_code == 200, erased.text
    assert erased.json()["user_id"] == user_id


def test_hidden_listing_drops_from_public_search(operator_client: TestClient) -> None:
    user = operator_client.post(
        "/api/v1/users",
        json={"email": _email("hide"), "is_active": True},
    )
    assert user.status_code == 201, user.text
    api_key = user.json()["api_key"]
    title = f"Hide-me-{uuid.uuid4().hex[:8]}"
    created = operator_client.post(
        "/api/v1/me/listings",
        headers={"X-API-Key": api_key},
        json={
            "title": title,
            "location": "Geneva",
            "price": 1800,
            "contact_url": "https://example.com/hide-me",
        },
    )
    assert created.status_code == 201, created.text
    listing_id = created.json()["id"]

    found = operator_client.get(
        "/api/v1/public/search?listing_type=housing&location=Geneva&limit=200"
    )
    assert found.status_code == 200, found.text
    assert any(item["title"] == title for item in found.json())

    hidden = operator_client.patch(
        f"/api/v1/admin/listings/{listing_id}/visibility",
        json={"is_hidden": True},
    )
    assert hidden.status_code == 200, hidden.text
    assert hidden.json()["is_hidden"] is True

    after = operator_client.get(
        "/api/v1/public/search?listing_type=housing&location=Geneva&limit=200"
    )
    assert after.status_code == 200, after.text
    assert all(item["title"] != title for item in after.json())

    listed = operator_client.get("/api/v1/admin/listings?hidden=true&owner_only=true")
    assert listed.status_code == 200, listed.text
    assert any(item["id"] == listing_id for item in listed.json())


def test_admin_free_alerts_toggle(operator_client: TestClient) -> None:
    created = operator_client.post(
        "/api/v1/users",
        json={"email": _email("alerts"), "is_active": True},
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]

    users = operator_client.get("/api/v1/admin/users?limit=50")
    assert users.status_code == 200, users.text
    row = next(item for item in users.json() if item["id"] == user_id)
    assert row["can_receive_alerts"] is False
    assert row["free_alerts_grandfathered"] is False

    granted = operator_client.patch(
        f"/api/v1/admin/users/{user_id}/free-alerts",
        json={"free_alerts_grandfathered": True},
    )
    assert granted.status_code == 200, granted.text
    assert granted.json()["free_alerts_grandfathered"] is True
    assert granted.json()["can_receive_alerts"] is True

    revoked = operator_client.patch(
        f"/api/v1/admin/users/{user_id}/free-alerts",
        json={"free_alerts_grandfathered": False},
    )
    assert revoked.status_code == 200, revoked.text
    assert revoked.json()["can_receive_alerts"] is False

    operator_client.delete(f"/api/v1/admin/users/{user_id}")


def test_admin_create_and_edit_listing(operator_client: TestClient) -> None:
    title = f"Admin-post-{uuid.uuid4().hex[:8]}"
    created = operator_client.post(
        "/api/v1/admin/listings",
        json={
            "listing_type": "housing",
            "title": title,
            "location": "Lausanne",
            "price": 2100,
            "contact_url": "https://example.com/admin-listing",
        },
    )
    assert created.status_code == 201, created.text
    listing_id = created.json()["id"]
    assert created.json()["provider_slug"] == "direct"

    found = operator_client.get(
        "/api/v1/public/search?listing_type=housing&location=Lausanne&limit=200"
    )
    assert found.status_code == 200, found.text
    assert any(item["title"] == title for item in found.json())

    updated_title = f"{title}-edited"
    updated = operator_client.patch(
        f"/api/v1/admin/listings/{listing_id}",
        json={"title": updated_title, "price": 2200},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == updated_title
    assert float(updated.json()["price"]) == 2200

    after = operator_client.get(
        "/api/v1/public/search?listing_type=housing&location=Lausanne&limit=200"
    )
    assert after.status_code == 200, after.text
    assert any(item["title"] == updated_title for item in after.json())

    hidden = operator_client.patch(
        f"/api/v1/admin/listings/{listing_id}/visibility",
        json={"is_hidden": True},
    )
    assert hidden.status_code == 200, hidden.text
    assert hidden.json()["is_hidden"] is True


def test_admin_insights(operator_client: TestClient) -> None:
    created = operator_client.post(
        "/api/v1/users",
        json={"email": _email("insights"), "is_active": True},
    )
    assert created.status_code == 201, created.text

    response = operator_client.get("/api/v1/admin/insights")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data["apps"], list)
    assert any(app["is_current"] for app in data["apps"])
    assert isinstance(data["active_boosts"], list)
    assert isinstance(data["signups_by_day"], list)
    assert len(data["signups_by_day"]) >= 1
    assert "configured" in data["stripe"]
    assert isinstance(data["stripe"]["payments_by_week"], list)

    operator_client.delete(f"/api/v1/admin/users/{created.json()['id']}")

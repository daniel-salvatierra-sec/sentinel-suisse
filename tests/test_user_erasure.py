"""Right-to-erasure tests (nLPD / GDPR)."""

import uuid

from fastapi.testclient import TestClient


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _create_user(client: TestClient, admin_auth: tuple[str, str], email: str) -> tuple[int, str]:
    response = client.post(
        "/api/v1/users",
        json={"email": email, "is_active": True},
        auth=admin_auth,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    return data["id"], data["api_key"]


def _create_saved_search(client: TestClient, api_key: str) -> int:
    response = client.post(
        "/api/v1/saved-searches",
        headers={"X-API-Key": api_key},
        json={
            "name": "Erasure test search",
            "query": {"location": "Geneva", "listing_type": "housing"},
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_email_channel(client: TestClient, api_key: str) -> int:
    response = client.post(
        "/api/v1/notification-channels",
        headers={"X-API-Key": api_key},
        json={
            "channel_type": "email",
            "channel_address": "erase-test@example.com",
            "is_primary": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_admin_erase_user_cascades_personal_data(
    client: TestClient, admin_auth: tuple[str, str]
) -> None:
    user_id, api_key = _create_user(client, admin_auth, _unique_email("admin-erase"))
    _create_saved_search(client, api_key)
    _create_email_channel(client, api_key)

    response = client.delete(f"/api/v1/users/{user_id}", auth=admin_auth)
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["user_id"] == user_id
    assert report["saved_searches_removed"] == 1
    assert report["notification_channels_removed"] == 1

    get_response = client.get(f"/api/v1/users/{user_id}", auth=admin_auth)
    assert get_response.status_code == 404

    saved_response = client.get("/api/v1/saved-searches", headers={"X-API-Key": api_key})
    assert saved_response.status_code == 401


def test_self_erase_user(client: TestClient, admin_auth: tuple[str, str]) -> None:
    user_id, api_key = _create_user(client, admin_auth, _unique_email("self-erase"))
    _create_saved_search(client, api_key)

    response = client.delete("/api/v1/users/me", headers={"X-API-Key": api_key})
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["user_id"] == user_id
    assert report["saved_searches_removed"] == 1

    get_response = client.get(f"/api/v1/users/{user_id}", auth=admin_auth)
    assert get_response.status_code == 404

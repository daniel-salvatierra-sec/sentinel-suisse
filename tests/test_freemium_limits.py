"""Freemium limits on saved searches and WhatsApp channel."""

import uuid

from fastapi.testclient import TestClient


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def test_free_user_blocked_on_second_saved_search(
    client: TestClient, admin_auth: tuple[str, str]
) -> None:
    created = client.post(
        "/api/v1/users",
        json={"email": _email("free-limit"), "is_active": True, "locale": "fr"},
        auth=admin_auth,
    )
    assert created.status_code == 201, created.text
    api_key = created.json()["api_key"]
    headers = {"X-API-Key": api_key}

    first = client.post(
        "/api/v1/saved-searches",
        headers=headers,
        json={
            "name": "First",
            "query": {"listing_type": "housing", "location": "Geneva"},
            "is_active": True,
        },
    )
    assert first.status_code == 201, first.text

    second = client.post(
        "/api/v1/saved-searches",
        headers=headers,
        json={
            "name": "Second",
            "query": {"listing_type": "job", "location": "Geneva"},
            "is_active": True,
        },
    )
    assert second.status_code == 403
    assert second.json()["detail"] == "saved_search_limit"


def test_premium_user_can_add_whatsapp_and_extra_search(
    client: TestClient, admin_auth: tuple[str, str]
) -> None:
    created = client.post(
        "/api/v1/users",
        json={
            "email": _email("prem"),
            "is_active": True,
            "locale": "fr",
            "is_premium": True,
        },
        auth=admin_auth,
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]
    api_key = created.json()["api_key"]
    headers = {"X-API-Key": api_key}

    assert created.json()["is_premium"] is True
    assert created.json()["saved_search_limit"] == 5

    wa = client.post(
        "/api/v1/notification-channels",
        headers=headers,
        json={
            "channel_type": "whatsapp",
            "channel_address": "+41791112233",
            "is_primary": False,
        },
    )
    assert wa.status_code == 201, wa.text

    for index in range(3):
        response = client.post(
            "/api/v1/saved-searches",
            headers=headers,
            json={
                "name": f"Search {index}",
                "query": {"listing_type": "housing", "location": "Geneva"},
                "is_active": True,
            },
        )
        assert response.status_code == 201, response.text

    patched = client.patch(
        f"/api/v1/users/{user_id}",
        json={"is_premium": False},
        auth=admin_auth,
    )
    assert patched.status_code == 200
    assert patched.json()["is_premium"] is False

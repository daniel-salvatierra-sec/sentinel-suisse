"""Alert dispatch and deduplication."""

import uuid

from fastapi.testclient import TestClient


def _admin_post_user(
    client: TestClient, admin_auth: tuple[str, str], email: str
) -> tuple[str, str]:
    response = client.post(
        "/api/v1/users",
        json={"email": email, "is_active": True},
        auth=admin_auth,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    return data["api_key"], data["id"]


def test_dispatch_sends_once_then_skips(client: TestClient, admin_auth: tuple[str, str]) -> None:
    listing = client.get("/api/v1/listings/1", auth=admin_auth)
    if listing.status_code == 404:
        import pytest

        pytest.skip("listing id=1 not in database")

    api_key, _user_id = _admin_post_user(
        client, admin_auth, f"alert-dispatch-{uuid.uuid4().hex[:8]}@example.com"
    )

    client.post(
        "/api/v1/saved-searches",
        headers={"X-API-Key": api_key},
        json={
            "name": "Geneva",
            "query": {"location": "Geneva", "listing_type": "housing"},
            "is_active": True,
        },
    )
    channel = client.post(
        "/api/v1/notification-channels",
        headers={"X-API-Key": api_key},
        json={
            "channel_type": "email",
            "channel_address": f"alert-dispatch-{uuid.uuid4().hex[:8]}@example.com",
            "is_primary": True,
        },
    )
    assert channel.status_code == 201, channel.text
    channel_id = channel.json()["id"]

    verify = client.patch(
        f"/api/v1/notification-channels/{channel_id}/verify",
        json={"is_verified": True},
        auth=admin_auth,
    )
    assert verify.status_code == 200, verify.text

    first = client.post("/api/v1/alerts/dispatch?listing_id=1", auth=admin_auth)
    assert first.status_code == 200, first.text
    assert first.json()["sent"] >= 1

    second = client.post("/api/v1/alerts/dispatch?listing_id=1", auth=admin_auth)
    assert second.status_code == 200, second.text
    assert second.json()["skipped"] >= 1

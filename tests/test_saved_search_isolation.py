"""Saved search isolation between users."""

from fastapi.testclient import TestClient


def _create_user(client: TestClient, admin_auth: tuple[str, str], email: str) -> tuple[int, str]:
    response = client.post(
        "/api/v1/users",
        json={"email": email, "is_active": True},
        auth=admin_auth,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    return data["id"], data["api_key"]


def _create_saved_search(client: TestClient, api_key: str, name: str) -> int:
    response = client.post(
        "/api/v1/saved-searches",
        headers={"X-API-Key": api_key},
        json={
            "name": name,
            "query": {"location": "Geneva", "listing_type": "housing"},
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_user_cannot_read_other_users_saved_search(
    client: TestClient, admin_auth: tuple[str, str]
) -> None:
    _, key_a = _create_user(client, admin_auth, "isolation-a@example.com")
    _, key_b = _create_user(client, admin_auth, "isolation-b@example.com")

    search_id = _create_saved_search(client, key_a, "Geneva alerts")

    response = client.get(
        f"/api/v1/saved-searches/{search_id}",
        headers={"X-API-Key": key_b},
    )
    assert response.status_code == 404

    own_response = client.get(
        f"/api/v1/saved-searches/{search_id}",
        headers={"X-API-Key": key_a},
    )
    assert own_response.status_code == 200
    assert own_response.json()["name"] == "Geneva alerts"


def test_user_only_sees_own_saved_searches(client: TestClient, admin_auth: tuple[str, str]) -> None:
    _, key_a = _create_user(client, admin_auth, "isolation-list-a@example.com")
    _, key_b = _create_user(client, admin_auth, "isolation-list-b@example.com")

    _create_saved_search(client, key_a, "Search A")
    _create_saved_search(client, key_b, "Search B")

    response_a = client.get("/api/v1/saved-searches", headers={"X-API-Key": key_a})
    assert response_a.status_code == 200
    names_a = {item["name"] for item in response_a.json()}
    assert "Search A" in names_a
    assert "Search B" not in names_a

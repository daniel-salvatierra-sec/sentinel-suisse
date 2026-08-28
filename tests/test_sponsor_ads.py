"""Manual sponsor placements (Phase 1 advertising)."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.api.auth import verify_admin


@pytest.fixture
def operator_client(client: TestClient) -> TestClient:
    client.app.dependency_overrides[verify_admin] = lambda: "admin"
    yield client
    client.app.dependency_overrides.pop(verify_admin, None)


def test_admin_sponsor_crud_and_public_feed(operator_client: TestClient) -> None:
    created = operator_client.post(
        "/api/v1/admin/sponsors",
        json={
            "sponsor_name": "Acme Language School",
            "context": "job",
            "headline": "Cursos de francés en Lausanne",
            "target_url": "https://example.com/acme",
            "monthly_chf": 250,
            "is_active": True,
            "sort_order": 1,
        },
    )
    assert created.status_code == 201, created.text
    sponsor_id = created.json()["id"]

    insights = operator_client.get("/api/v1/admin/insights")
    assert insights.status_code == 200, insights.text
    assert insights.json()["sponsors"]["active_count"] >= 1
    assert Decimal(str(insights.json()["sponsors"]["estimated_monthly_chf"])) >= Decimal("250")

    public = operator_client.get("/api/v1/public/sponsors?context=job")
    assert public.status_code == 200, public.text
    items = public.json()
    assert any(item["id"] == sponsor_id for item in items)

    event = operator_client.post(
        f"/api/v1/public/sponsors/{sponsor_id}/events",
        json={"kind": "click"},
    )
    assert event.status_code == 204, event.text

    listed = operator_client.get("/api/v1/admin/sponsors")
    assert listed.status_code == 200, listed.text
    row = next(item for item in listed.json() if item["id"] == sponsor_id)
    assert row["click_count"] == 1

    deleted = operator_client.delete(f"/api/v1/admin/sponsors/{sponsor_id}")
    assert deleted.status_code == 204, deleted.text


def test_sponsor_requires_headline_or_image(operator_client: TestClient) -> None:
    response = operator_client.post(
        "/api/v1/admin/sponsors",
        json={
            "sponsor_name": "Empty",
            "target_url": "https://example.com/empty",
        },
    )
    assert response.status_code == 422

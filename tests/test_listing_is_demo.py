"""ListingRead.is_demo derived from raw_payload."""

from datetime import UTC, datetime
from types import SimpleNamespace

from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.schemas.listing import ListingRead, listing_is_demo


def _base_fields(**overrides: object) -> dict:
    data = {
        "id": 1,
        "provider_id": 1,
        "external_id": "jc-demo-001",
        "listing_type": ListingType.JOB,
        "title": "Software Engineer",
        "description": None,
        "location": "Geneva",
        "price": None,
        "source_url": "https://www.jobs.ch/en/vacancies/detail/jc-demo-001/",
        "content_hash": "a" * 64,
        "fetched_at": datetime.now(UTC),
    }
    data.update(overrides)
    return data


def test_listing_is_demo_helper() -> None:
    assert listing_is_demo({"pilot": True}) is True
    assert listing_is_demo({"source": "fixture"}) is True
    assert listing_is_demo({"source": "jobs", "pilot": False}) is False
    assert listing_is_demo(None) is False
    assert listing_is_demo({}) is False


def test_listing_read_is_demo_from_dict() -> None:
    demo = ListingRead.model_validate(
        _base_fields(raw_payload={"source": "fixture", "pilot": True})
    )
    assert demo.is_demo is True
    dumped = demo.model_dump()
    assert dumped["is_demo"] is True
    assert "raw_payload" not in dumped

    live = ListingRead.model_validate(_base_fields(raw_payload={"source": "jobs"}))
    assert live.is_demo is False


def test_listing_read_is_demo_from_orm_namespace() -> None:
    orm = SimpleNamespace(**_base_fields(raw_payload={"pilot": True, "source": "fixture"}))
    read = ListingRead.model_validate(orm)
    assert read.is_demo is True

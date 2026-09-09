"""RawListing must ignore bogus workload values so ingest cannot abort mid-run."""

from sentinel_suisse.ingest.schemas import RawListing, _normalize_workload_percent
from sentinel_suisse.models.enums import ListingType


def test_normalize_workload_drops_out_of_range() -> None:
    assert _normalize_workload_percent(80) == 80
    assert _normalize_workload_percent(0) == 0
    assert _normalize_workload_percent(100) == 100
    assert _normalize_workload_percent(360) is None
    assert _normalize_workload_percent(-1) is None
    assert _normalize_workload_percent("nope") is None


def test_raw_listing_accepts_jobup_style_bogus_pensum() -> None:
    listing = RawListing(
        external_id="ju-360",
        listing_type=ListingType.JOB,
        title="Logistics coordinator",
        source_url="https://www.jobup.ch/fr/emplois/detail/ju-360/",
        workload_min=360,
        workload_max=100,
    )
    assert listing.workload_min is None
    assert listing.workload_max == 100

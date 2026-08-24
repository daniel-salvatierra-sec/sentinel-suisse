"""Normalize phone numbers and https URLs for direct listings."""

from sentinel_suisse.schemas.direct_listing import DirectListingCreate
from sentinel_suisse.services.contact_link import ContactLinkError, normalize_contact_link


def test_swiss_mobile_becomes_whatsapp() -> None:
    assert normalize_contact_link("079 123 45 67") == "https://wa.me/41791234567"


def test_plus_forty_one_becomes_whatsapp() -> None:
    assert normalize_contact_link("+41 79 123 45 67") == "https://wa.me/41791234567"


def test_https_url_is_kept() -> None:
    assert normalize_contact_link("https://example.com/apply") == "https://example.com/apply"


def test_schema_accepts_phone() -> None:
    payload = DirectListingCreate(
        listing_type="job",
        title="Chofer de bus Geneva",
        location="Geneva",
        job_category="logistics",
        contact_url="0791234567",
    )
    assert payload.contact_url == "https://wa.me/41791234567"


def test_short_contact_is_rejected() -> None:
    try:
        normalize_contact_link("123")
    except ContactLinkError:
        return
    raise AssertionError("expected ContactLinkError")

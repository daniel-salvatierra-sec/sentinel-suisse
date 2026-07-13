"""Localized alert template tests."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from sentinel_suisse.i18n.alerts import format_email_alert, format_whatsapp_alert
from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.notifications.base import AlertMessage

ALL_LANGUAGES = ("fr", "de", "es", "pt", "en")

EMAIL_MARKERS = {
    "fr": "Lieu",
    "de": "Ort",
    "es": "Ubicación",
    "pt": "Localização",
    "en": "Location",
}


def _message(locale: str) -> AlertMessage:
    listing = Listing(
        id=1,
        provider_id=1,
        external_id="x",
        listing_type=ListingType.HOUSING,
        title="Studio Geneva",
        location="Geneva",
        price=Decimal("1200"),
        source_url="https://example.com/listing",
        content_hash="a" * 64,
        fetched_at=datetime.now(UTC),
    )
    saved_search = SavedSearch(
        id=1,
        user_id=1,
        name="Geneva",
        query={"location": "Geneva"},
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return AlertMessage(
        listing=listing,
        saved_search=saved_search,
        channel_address="user@example.com",
        channel_type="email",
        locale=locale,
    )


@pytest.mark.parametrize("locale", ALL_LANGUAGES)
def test_email_alert_localized_labels(locale: str) -> None:
    _subject, body = format_email_alert(_message(locale))
    assert EMAIL_MARKERS[locale] in body
    assert "Studio Geneva" in body
    assert "https://example.com/listing" in body


@pytest.mark.parametrize("locale", ALL_LANGUAGES)
def test_whatsapp_alert_includes_listing_title(locale: str) -> None:
    body = format_whatsapp_alert(_message(locale))
    assert "Studio Geneva" in body
    assert "*Geneva*" in body


def test_email_alert_falls_back_to_french_for_unknown_locale() -> None:
    message = _message("xx")
    _subject, body = format_email_alert(message)
    assert "Lieu" in body

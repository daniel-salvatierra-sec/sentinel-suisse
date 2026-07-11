"""Email notifier tests."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from sentinel_suisse.config import Settings
from sentinel_suisse.models.enums import ChannelType, ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.notifications.base import AlertMessage
from sentinel_suisse.notifications.email import EmailNotifier
from sentinel_suisse.notifications.factory import get_notifier_for_channel


def _message() -> AlertMessage:
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
    )


def test_factory_uses_console_when_smtp_missing() -> None:
    settings = Settings(notifier_mode="auto", smtp_host="", smtp_from="")
    notifier = get_notifier_for_channel(ChannelType.EMAIL, settings=settings)
    assert notifier.__class__.__name__ == "ConsoleNotifier"


def test_factory_uses_email_when_smtp_configured() -> None:
    settings = Settings(
        notifier_mode="auto",
        smtp_host="smtp.example.com",
        smtp_from="alerts@example.com",
    )
    notifier = get_notifier_for_channel(ChannelType.EMAIL, settings=settings)
    assert notifier.__class__.__name__ == "EmailNotifier"


@patch("sentinel_suisse.notifications.email.smtplib.SMTP")
def test_email_notifier_sends_message(mock_smtp: MagicMock) -> None:
    settings = Settings(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="user",
        smtp_password="pass",  # noqa: S106
        smtp_from="alerts@example.com",
        smtp_use_tls=True,
    )
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance

    EmailNotifier(settings).send(_message())

    mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=30)
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with("user", "pass")
    smtp_instance.send_message.assert_called_once()

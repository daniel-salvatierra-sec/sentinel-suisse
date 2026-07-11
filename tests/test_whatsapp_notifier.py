"""WhatsApp notifier tests."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from sentinel_suisse.config import Settings
from sentinel_suisse.models.enums import ChannelType, ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.notifications.base import AlertMessage
from sentinel_suisse.notifications.factory import get_notifier_for_channel
from sentinel_suisse.notifications.whatsapp import WhatsAppNotifier, _normalize_phone


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
        channel_address="+41791234567",
        channel_type="whatsapp",
    )


def test_normalize_phone_strips_formatting() -> None:
    assert _normalize_phone("+41 79 123 45 67") == "41791234567"


def test_factory_uses_console_when_whatsapp_missing() -> None:
    settings = Settings(whatsapp_token="", whatsapp_phone_number_id="")
    notifier = get_notifier_for_channel(ChannelType.WHATSAPP, settings=settings)
    assert notifier.__class__.__name__ == "ConsoleNotifier"


def test_factory_uses_whatsapp_when_configured() -> None:
    settings = Settings(whatsapp_token="token", whatsapp_phone_number_id="123456")  # noqa: S106
    notifier = get_notifier_for_channel(ChannelType.WHATSAPP, settings=settings)
    assert notifier.__class__.__name__ == "WhatsAppNotifier"


@patch("sentinel_suisse.notifications.whatsapp.httpx.post")
def test_whatsapp_notifier_sends_message(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    settings = Settings(whatsapp_token="test-token", whatsapp_phone_number_id="999888")  # noqa: S106
    WhatsAppNotifier(settings).send(_message())

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer test-token"
    assert call_kwargs["json"]["to"] == "41791234567"
    assert call_kwargs["json"]["type"] == "text"

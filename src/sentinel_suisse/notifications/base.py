"""Notification channel interface."""

from dataclasses import dataclass

from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.saved_search import SavedSearch


@dataclass(frozen=True)
class AlertMessage:
    listing: Listing
    saved_search: SavedSearch
    channel_address: str
    channel_type: str
    locale: str = DEFAULT_LANGUAGE


class Notifier:
    def send(self, message: AlertMessage) -> None:
        raise NotImplementedError

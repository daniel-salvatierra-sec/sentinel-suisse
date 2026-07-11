"""Pilot notifier — logs alerts to stdout (no external API)."""

import logging

from sentinel_suisse.notifications.base import AlertMessage, Notifier

logger = logging.getLogger(__name__)


class ConsoleNotifier(Notifier):
    def send(self, message: AlertMessage) -> None:
        listing = message.listing
        logger.info(
            "ALERT [%s] search=%r title=%r location=%r price=%s url=%s",
            message.channel_address,
            message.saved_search.name,
            listing.title,
            listing.location,
            listing.price,
            listing.source_url,
        )

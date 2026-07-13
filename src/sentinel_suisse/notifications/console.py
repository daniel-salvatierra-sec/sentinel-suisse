"""Pilot notifier — logs alerts to stdout (no external API)."""

import logging

from sentinel_suisse.i18n.alerts import format_console_summary
from sentinel_suisse.notifications.base import AlertMessage, Notifier

logger = logging.getLogger(__name__)


class ConsoleNotifier(Notifier):
    def send(self, message: AlertMessage) -> None:
        listing = message.listing
        logger.info(
            "ALERT [%s] %s | title=%r location=%r price=%s",
            message.channel_address,
            format_console_summary(message),
            listing.title,
            listing.location,
            listing.price,
        )

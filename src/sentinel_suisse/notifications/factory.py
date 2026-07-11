"""Select notifier implementation for a channel type."""

from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.models.enums import ChannelType
from sentinel_suisse.notifications.base import Notifier
from sentinel_suisse.notifications.console import ConsoleNotifier
from sentinel_suisse.notifications.email import EmailNotifier


def get_notifier_for_channel(
    channel_type: ChannelType, settings: Settings | None = None
) -> Notifier:
    cfg = settings or get_settings()
    if cfg.notifier_mode == "console":
        return ConsoleNotifier()
    if cfg.notifier_mode == "smtp" and not cfg.smtp_is_configured():
        msg = "SMTP is not configured (set SMTP_HOST and SMTP_FROM)"
        raise RuntimeError(msg)
    if channel_type == ChannelType.EMAIL and cfg.smtp_is_configured():
        return EmailNotifier(cfg)
    return ConsoleNotifier()

"""WhatsApp Cloud API notifier (Meta Graph API)."""

import re

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.i18n.alerts import format_whatsapp_alert
from sentinel_suisse.notifications.base import AlertMessage, Notifier

_GRAPH_API_VERSION = "v21.0"


def _normalize_phone(address: str) -> str:
    return re.sub(r"\D", "", address)


class WhatsAppNotifier(Notifier):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, message: AlertMessage) -> None:
        phone = _normalize_phone(message.channel_address)
        if not phone:
            msg = "Invalid WhatsApp phone number"
            raise ValueError(msg)

        url = (
            f"https://graph.facebook.com/{_GRAPH_API_VERSION}/"
            f"{self._settings.whatsapp_phone_number_id}/messages"
        )
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {self._settings.whatsapp_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": format_whatsapp_alert(message)},
            },
            timeout=30.0,
        )
        response.raise_for_status()

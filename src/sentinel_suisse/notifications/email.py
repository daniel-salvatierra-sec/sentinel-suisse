"""SMTP email notifier."""

import smtplib
from email.message import EmailMessage

from sentinel_suisse.config import Settings
from sentinel_suisse.notifications.base import AlertMessage, Notifier


class EmailNotifier(Notifier):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, message: AlertMessage) -> None:
        listing = message.listing
        body = (
            f"New match for saved search: {message.saved_search.name}\n\n"
            f"{listing.title}\n"
            f"Location: {listing.location}\n"
            f"Price: {listing.price}\n"
            f"Link: {listing.source_url}\n"
        )
        email = EmailMessage()
        email["Subject"] = f"Sentinel Suisse: {listing.title}"[:120]
        email["From"] = self._settings.smtp_from
        email["To"] = message.channel_address
        email.set_content(body)

        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port, timeout=30) as smtp:
            if self._settings.smtp_use_tls:
                smtp.starttls()
            if self._settings.smtp_user:
                smtp.login(self._settings.smtp_user, self._settings.smtp_password)
            smtp.send_message(email)

"""SMTP email notifier."""

import smtplib
from email.message import EmailMessage

from sentinel_suisse.config import Settings
from sentinel_suisse.i18n.alerts import format_email_alert, listing_app_url
from sentinel_suisse.notifications.base import AlertMessage, Notifier
from sentinel_suisse.notifications.email_html import build_html_email


class EmailNotifier(Notifier):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, message: AlertMessage) -> None:
        app_url = self._settings.public_app_url
        subject, body = format_email_alert(message, app_url=app_url)
        email = EmailMessage()
        email["Subject"] = subject
        email["From"] = self._settings.smtp_from
        email["To"] = message.channel_address
        email.set_content(body)
        primary = listing_app_url(app_url, message.listing.id) or message.listing.source_url
        email.add_alternative(build_html_email(body, primary), subtype="html")

        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port, timeout=30) as smtp:
            if self._settings.smtp_use_tls:
                smtp.starttls()
            if self._settings.smtp_user:
                smtp.login(self._settings.smtp_user, self._settings.smtp_password)
            smtp.send_message(email)

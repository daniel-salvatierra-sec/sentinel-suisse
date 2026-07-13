"""SMTP email notifier."""

import smtplib
from email.message import EmailMessage

from sentinel_suisse.config import Settings
from sentinel_suisse.i18n.alerts import format_email_alert
from sentinel_suisse.notifications.base import AlertMessage, Notifier


class EmailNotifier(Notifier):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, message: AlertMessage) -> None:
        subject, body = format_email_alert(message)
        email = EmailMessage()
        email["Subject"] = subject
        email["From"] = self._settings.smtp_from
        email["To"] = message.channel_address
        email.set_content(body)

        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port, timeout=30) as smtp:
            if self._settings.smtp_use_tls:
                smtp.starttls()
            if self._settings.smtp_user:
                smtp.login(self._settings.smtp_user, self._settings.smtp_password)
            smtp.send_message(email)

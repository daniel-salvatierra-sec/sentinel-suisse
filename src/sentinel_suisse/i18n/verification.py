"""Email verification copy in five mandatory languages."""

from sentinel_suisse.i18n import resolve_locale

_VERIFY_COPY: dict[str, dict[str, str]] = {
    "fr": {
        "subject": "Suisse Alert — confirmez votre e-mail",
        "body": (
            "Bonjour,\n\n"
            "Confirmez votre adresse e-mail pour activer les alertes Suisse Alert :\n\n"
            "{url}\n\n"
            "Ce lien expire dans {hours} heures.\n\n"
            "Si vous n'avez pas demandé cette alerte, ignorez ce message."
        ),
    },
    "de": {
        "subject": "Suisse Alert — E-Mail bestätigen",
        "body": (
            "Hallo,\n\n"
            "Bestätigen Sie Ihre E-Mail-Adresse, um Suisse Alert-Benachrichtigungen "
            "zu aktivieren:\n\n"
            "{url}\n\n"
            "Dieser Link läuft in {hours} Stunden ab.\n\n"
            "Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail."
        ),
    },
    "es": {
        "subject": "Suisse Alert — confirma tu email",
        "body": (
            "Hola,\n\n"
            "Confirma tu dirección de email para activar las alertas de Suisse Alert:\n\n"
            "{url}\n\n"
            "Este enlace caduca en {hours} horas.\n\n"
            "Si no solicitaste esta alerta, ignora este mensaje."
        ),
    },
    "pt": {
        "subject": "Suisse Alert — confirme o seu email",
        "body": (
            "Olá,\n\n"
            "Confirme o seu endereço de email para ativar alertas Suisse Alert:\n\n"
            "{url}\n\n"
            "Esta ligação expira em {hours} horas.\n\n"
            "Se não pediu esta alerta, ignore esta mensagem."
        ),
    },
    "en": {
        "subject": "Suisse Alert — confirm your email",
        "body": (
            "Hello,\n\n"
            "Confirm your email address to enable Suisse Alert notifications:\n\n"
            "{url}\n\n"
            "This link expires in {hours} hours.\n\n"
            "If you did not request this alert, please ignore this email."
        ),
    },
}


def format_verification_email(locale: str, url: str, *, ttl_hours: int) -> tuple[str, str]:
    lang = resolve_locale(locale)
    copy = _VERIFY_COPY[lang]
    body = copy["body"].format(url=url, hours=ttl_hours)
    return copy["subject"], body

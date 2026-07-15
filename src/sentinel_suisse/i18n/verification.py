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
        "whatsapp": (
            "Suisse Alert : confirmez vos alertes via ce lien :\n{url}\n"
            "Ou répondez {keyword} à ce numéro.\n"
            "(expire dans {hours} heures)"
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
        "whatsapp": (
            "Suisse Alert: Bestätigen Sie Ihre Alerts über diesen Link:\n{url}\n"
            "Oder antworten Sie {keyword} an diese Nummer.\n"
            "(läuft in {hours} Stunden ab)"
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
        "whatsapp": (
            "Suisse Alert: confirma tus alertas con este enlace:\n{url}\n"
            "O responde {keyword} a este número.\n"
            "(caduca en {hours} horas)"
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
        "whatsapp": (
            "Suisse Alert: confirme as suas alertas com esta ligação:\n{url}\n"
            "Ou responda {keyword} a este número.\n"
            "(expira em {hours} horas)"
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
        "whatsapp": (
            "Suisse Alert: confirm your alerts by opening this link:\n{url}\n"
            "Or reply {keyword} to this number.\n"
            "(expires in {hours} hours)"
        ),
    },
}


def format_verification_whatsapp(
    locale: str,
    url: str,
    *,
    ttl_hours: int,
    keyword: str = "OK",
) -> str:
    lang = resolve_locale(locale)
    copy = _VERIFY_COPY[lang]
    whatsapp_template = copy.get(
        "whatsapp",
        _VERIFY_COPY["en"]["whatsapp"],
    )
    return whatsapp_template.format(
        url=url,
        hours=ttl_hours,
        keyword=keyword.strip() or "OK",
    )


def format_verification_email(locale: str, url: str, *, ttl_hours: int) -> tuple[str, str]:
    lang = resolve_locale(locale)
    copy = _VERIFY_COPY[lang]
    body = copy["body"].format(url=url, hours=ttl_hours)
    return copy["subject"], body

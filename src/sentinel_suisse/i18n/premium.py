"""Premium welcome email — five languages, informal register."""

from sentinel_suisse.i18n import resolve_locale

_COPY: dict[str, dict[str, str]] = {
    "fr": {
        "subject": "Ton Premium est actif — LinkSwiss",
        "body": (
            "Bonjour,\n\n"
            "Ton Premium est actif. Sentinela t'alerte dès qu'une offre correspond.\n\n"
            "{url}\n"
        ),
    },
    "de": {
        "subject": "Dein Premium ist aktiv — LinkSwiss",
        "body": (
            "Hallo,\n\n"
            "Dein Premium ist aktiv. Sentinela warnt dich, sobald ein Angebot zu dir passt.\n\n"
            "{url}\n"
        ),
    },
    "es": {
        "subject": "Ya eres Premium — LinkSwiss",
        "body": (
            "Hola,\n\n"
            "Ya eres Premium. Sentinela te avisa cuando una oferta encaje.\n\n"
            "{url}\n"
        ),
    },
    "pt": {
        "subject": "Já és Premium — LinkSwiss",
        "body": (
            "Olá,\n\n"
            "Já és Premium. A Sentinela avisa-te quando uma oferta encaixar.\n\n"
            "{url}\n"
        ),
    },
    "en": {
        "subject": "You are Premium — LinkSwiss",
        "body": (
            "Hello,\n\n"
            "You are Premium. Sentinela will alert you when an offer fits.\n\n"
            "{url}\n"
        ),
    },
}


def format_premium_welcome(locale: str | None, app_url: str) -> tuple[str, str]:
    copy = _COPY[resolve_locale(locale)]
    url = app_url.rstrip("/")
    return copy["subject"], copy["body"].format(url=url)

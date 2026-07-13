"""Supported UI and legal document languages."""

SUPPORTED_LANGUAGES = frozenset({"fr", "de", "es", "pt", "en"})
DEFAULT_LANGUAGE = "fr"


def resolve_locale(locale: str | None) -> str:
    if locale and locale in SUPPORTED_LANGUAGES:
        return locale
    return DEFAULT_LANGUAGE

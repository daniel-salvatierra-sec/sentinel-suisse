"""Supported UI and legal document languages."""

SUPPORTED_LANGUAGES = frozenset({"fr", "de", "es", "pt", "en"})
DEFAULT_LANGUAGE = "fr"

# BCP-47-ish codes used in API query params and file suffixes
LanguageCode = str  # fr | de | es | pt | en

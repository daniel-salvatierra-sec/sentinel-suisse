"""Load published terms of service documents."""

from sentinel_suisse.config import PROJECT_DIR
from sentinel_suisse.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

TERMS_DIR = PROJECT_DIR / "docs" / "legal"
TERMS_VERSION = "2026-07-16"
SUPPORTED_LANGS = SUPPORTED_LANGUAGES


def load_terms_of_service(lang: str) -> str:
    if lang not in SUPPORTED_LANGS:
        msg = f"Unsupported language: {lang}"
        raise ValueError(msg)

    path = TERMS_DIR / f"terms.{lang}.md"
    if not path.is_file():
        msg = f"Terms of service file not found: {path}"
        raise FileNotFoundError(msg)

    return path.read_text(encoding="utf-8")


def default_language() -> str:
    return DEFAULT_LANGUAGE

"""Load published privacy policy documents."""

from sentinel_suisse.config import PROJECT_DIR

PRIVACY_DIR = PROJECT_DIR / "docs" / "privacy"
POLICY_VERSION = "2026-07-13"
SUPPORTED_LANGS = frozenset({"fr", "de"})


def load_privacy_policy(lang: str) -> str:
    if lang not in SUPPORTED_LANGS:
        msg = f"Unsupported language: {lang}"
        raise ValueError(msg)

    path = PRIVACY_DIR / f"privacy-policy.{lang}.md"
    if not path.is_file():
        msg = f"Privacy policy file not found: {path}"
        raise FileNotFoundError(msg)

    return path.read_text(encoding="utf-8")

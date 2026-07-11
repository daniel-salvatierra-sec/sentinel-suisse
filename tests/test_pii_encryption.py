"""Unit tests for PII encryption helpers."""

import pytest
from cryptography.fernet import Fernet

from sentinel_suisse.config import get_settings
from sentinel_suisse.security.pii import decrypt_pii, email_lookup, encrypt_pii

_TEST_KEY = Fernet.generate_key().decode()


@pytest.fixture(autouse=True)
def _pii_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PII_ENCRYPTION_KEY", _TEST_KEY)
    get_settings.cache_clear()


def test_encrypt_decrypt_roundtrip() -> None:
    plain = "user@example.com"
    encrypted = encrypt_pii(plain)
    assert encrypted != plain
    assert encrypted.startswith("gAAAA")
    assert decrypt_pii(encrypted) == plain


def test_decrypt_legacy_plaintext() -> None:
    assert decrypt_pii("legacy-plain@example.com") == "legacy-plain@example.com"


def test_email_lookup_deterministic_and_case_insensitive() -> None:
    a = email_lookup("User@Example.COM")
    b = email_lookup("user@example.com")
    assert a == b
    assert len(a) == 64


def test_email_lookup_differs_for_different_emails() -> None:
    assert email_lookup("a@example.com") != email_lookup("b@example.com")

"""PII encryption at rest (Fernet)."""

import hashlib
import hmac

from cryptography.fernet import Fernet, InvalidToken

from sentinel_suisse.config import get_settings

_FERNET_PREFIX = "gAAAA"


def _fernet() -> Fernet:
    settings = get_settings()
    if not settings.pii_encryption_key:
        msg = "PII_ENCRYPTION_KEY is not configured"
        raise RuntimeError(msg)
    return Fernet(settings.pii_encryption_key.encode("utf-8"))


def encrypt_pii(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_pii(ciphertext: str) -> str:
    if not ciphertext.startswith(_FERNET_PREFIX):
        return ciphertext
    try:
        return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        msg = "Failed to decrypt PII field"
        raise ValueError(msg) from exc


def email_lookup(email: str) -> str:
    settings = get_settings()
    key = settings.pii_encryption_key or settings.secret_key or "sentinel-dev-lookup-key"
    normalized = email.strip().lower()
    return hmac.new(key.encode("utf-8"), normalized.encode("utf-8"), hashlib.sha256).hexdigest()

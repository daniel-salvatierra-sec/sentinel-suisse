"""Generate Fernet key for PII_ENCRYPTION_KEY in .env.

Usage (never commit the key):
    python scripts/generate_pii_key.py
"""

from cryptography.fernet import Fernet


def main() -> None:
    key = Fernet.generate_key().decode("utf-8")
    print("\nAdd to .env (do not commit):\n")
    print(f"PII_ENCRYPTION_KEY={key}")


if __name__ == "__main__":
    main()

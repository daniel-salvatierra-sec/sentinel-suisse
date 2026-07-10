"""Generate bcrypt hash for ADMIN_PASSWORD_HASH in .env.

Usage (never commit the password):
    python scripts/generate_admin_hash.py
"""

import getpass

import bcrypt


def main() -> None:
    password = getpass.getpass("Admin password (input hidden): ")
    if len(password) < 12:
        print("Use at least 12 characters.")
        return
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match.")
        return
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    print("\nAdd to .env (do not commit):\n")
    print(f"ADMIN_PASSWORD_HASH={hashed}")


if __name__ == "__main__":
    main()

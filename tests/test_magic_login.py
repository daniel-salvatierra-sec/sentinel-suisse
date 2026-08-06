"""Tests for the passwordless magic-login flow."""

import re
import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app
from sentinel_suisse.security.verification_tokens import create_login_token


def _unique_email() -> str:
    return f"login-{uuid.uuid4().hex[:10]}@example.com"


@pytest.fixture
def dev_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("TRUSTED_HOSTS", "")
    get_settings.cache_clear()
    return TestClient(create_app())


def _signup(dev_client: TestClient, email: str) -> str:
    payload = {
        "email": email,
        "locale": "fr",
        "consent": True,
        "query": {"listing_type": "housing", "location": "Geneva"},
    }
    response = dev_client.post("/api/v1/public/signup", json=payload)
    assert response.status_code == 201, response.text
    return str(response.json()["api_key"])


def test_login_request_unknown_email_returns_generic_success(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    response = dev_client.post(
        "/api/v1/public/login",
        json={"email": _unique_email(), "locale": "fr"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["sent"] is True


def test_login_request_known_email_logs_link(
    dev_client: TestClient,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    email = _unique_email()
    _signup(dev_client, email)

    # Force the "no SMTP configured" fallback path regardless of the local
    # dev .env, so this test is deterministic and never sends a real email.
    monkeypatch.setenv("SMTP_HOST", "")
    get_settings.cache_clear()
    no_smtp_settings = get_settings()

    from sentinel_suisse.db.session import SessionLocal
    from sentinel_suisse.services.magic_login import request_magic_login

    db = SessionLocal()
    try:
        with caplog.at_level("INFO"):
            request_magic_login(db, no_smtp_settings, email, "fr")
    finally:
        db.close()
        get_settings.cache_clear()

    match = re.search(r"MAGIC LOGIN EMAIL to=\S+ url=(\S+)", caplog.text)
    assert match, "expected the login link to be logged when SMTP is not configured"


def test_login_confirm_issues_working_api_key(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    email = _unique_email()
    old_api_key = _signup(dev_client, email)

    from sentinel_suisse.db.session import SessionLocal
    from sentinel_suisse.models.user import User
    from sentinel_suisse.security.pii import email_lookup

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email_lookup == email_lookup(email)).one()
        token = create_login_token(
            user_id=user.id,
            secret=settings.secret_key or settings.pii_encryption_key,
            ttl_minutes=settings.login_token_ttl_minutes,
        )
    finally:
        db.close()

    confirm = dev_client.post("/api/v1/public/login/confirm", json={"token": token})
    assert confirm.status_code == 200, confirm.text
    new_api_key = confirm.json()["api_key"]
    assert new_api_key != old_api_key

    old_key_check = dev_client.get("/api/v1/users/me", headers={"X-API-Key": old_api_key})
    assert old_key_check.status_code == 401

    new_key_check = dev_client.get("/api/v1/users/me", headers={"X-API-Key": new_api_key})
    assert new_key_check.status_code == 200


def test_login_confirm_rejects_invalid_token(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    response = dev_client.post("/api/v1/public/login/confirm", json={"token": "not-a-real-token"})
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid_token"

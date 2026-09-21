"""Tests for email+password login and set-password flow."""

import uuid

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app
from sentinel_suisse.security.verification_tokens import (
    create_login_token,
    create_set_password_token,
)


def _unique_email() -> str:
    return f"login-{uuid.uuid4().hex[:10]}@example.com"


@pytest.fixture
def dev_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("TRUSTED_HOSTS", "")
    get_settings.cache_clear()
    return TestClient(create_app())


def _signup(dev_client: TestClient, email: str, password: str = "testpass12") -> str:  # noqa: S107
    payload = {
        "email": email,
        "password": password,
        "locale": "fr",
        "consent": True,
        "query": {"listing_type": "housing", "location": "Geneva"},
    }
    response = dev_client.post("/api/v1/public/signup", json=payload)
    assert response.status_code == 201, response.text
    return str(response.json()["api_key"])


def test_login_unknown_email_returns_invalid_credentials(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    response = dev_client.post(
        "/api/v1/public/login",
        json={"email": _unique_email(), "password": "testpass12", "locale": "fr"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["invalid_credentials"] is True
    assert data.get("api_key") is None


def test_login_with_password_returns_session(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    email = _unique_email()
    password = "testpass12"  # noqa: S105
    old_api_key = _signup(dev_client, email, password)

    response = dev_client.post(
        "/api/v1/public/login",
        json={"email": email, "password": password, "locale": "fr"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["sent"] is False
    assert data["api_key"]
    assert data["api_key"] != old_api_key
    assert data["device_token"]
    me = dev_client.get("/api/v1/users/me", headers={"X-API-Key": data["api_key"]})
    assert me.status_code == 200


def test_login_wrong_password_rejected(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    email = _unique_email()
    _signup(dev_client, email, "testpass12")

    response = dev_client.post(
        "/api/v1/public/login",
        json={"email": email, "password": "wrongpass99", "locale": "fr"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["invalid_credentials"] is True
    assert data.get("api_key") is None


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
    body = confirm.json()
    new_api_key = body["api_key"]
    assert new_api_key != old_api_key
    assert body.get("device_token")

    old_key_check = dev_client.get("/api/v1/users/me", headers={"X-API-Key": old_api_key})
    assert old_key_check.status_code == 401

    new_key_check = dev_client.get("/api/v1/users/me", headers={"X-API-Key": new_api_key})
    assert new_key_check.status_code == 200


def test_set_password_from_token(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    email = _unique_email()
    _signup(dev_client, email, "oldpass123")

    from sentinel_suisse.db.session import SessionLocal
    from sentinel_suisse.models.user import User
    from sentinel_suisse.security.pii import email_lookup

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email_lookup == email_lookup(email)).one()
        # Simulate legacy account without password
        user.password_hash = None
        db.commit()
        token = create_set_password_token(
            user_id=user.id,
            secret=settings.secret_key or settings.pii_encryption_key,
            ttl_minutes=settings.login_token_ttl_minutes,
        )
    finally:
        db.close()

    response = dev_client.post(
        "/api/v1/public/login/set-password",
        json={"token": token, "password": "newpass123"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["api_key"]
    assert data["device_token"]

    login = dev_client.post(
        "/api/v1/public/login",
        json={"email": email, "password": "newpass123", "locale": "fr"},
    )
    assert login.status_code == 200
    assert login.json()["api_key"]


def test_forgot_password_generic_success(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    response = dev_client.post(
        "/api/v1/public/login/forgot",
        json={"email": _unique_email(), "locale": "fr"},
    )
    assert response.status_code == 200
    assert response.json()["sent"] is True


def test_login_confirm_rejects_invalid_token(dev_client: TestClient) -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")

    response = dev_client.post("/api/v1/public/login/confirm", json={"token": "not-a-real-token"})
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid_token"

"""Pytest fixtures for API integration tests."""

import os

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app

# Stable test key so integration tests can encrypt/decrypt without a real .env secret.
_TEST_PII_KEY = os.environ.get("PII_ENCRYPTION_KEY") or Fernet.generate_key().decode()
os.environ.setdefault("PII_ENCRYPTION_KEY", _TEST_PII_KEY)


@pytest.fixture(scope="session", autouse=True)
def _ensure_pii_key() -> None:
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _test_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate tests from production values in the local .env file."""
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("TRUSTED_HOSTS", "")
    get_settings.cache_clear()
    limiter.reset()


@pytest.fixture
def client() -> TestClient:
    get_settings.cache_clear()
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")
    return TestClient(create_app())


@pytest.fixture
def admin_auth() -> tuple[str, str]:
    settings = get_settings()
    if not settings.admin_username or not settings.admin_password_hash:
        pytest.skip("Admin credentials not configured in .env")
    password = os.getenv("TEST_ADMIN_PASSWORD")
    if not password:
        pytest.skip("TEST_ADMIN_PASSWORD not set for integration tests")
    return settings.admin_username, password

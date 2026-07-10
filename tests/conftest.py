"""Pytest fixtures for API integration tests."""

import os

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import app


@pytest.fixture
def client() -> TestClient:
    get_settings.cache_clear()
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured in .env")
    return TestClient(app)


@pytest.fixture
def admin_auth() -> tuple[str, str]:
    settings = get_settings()
    if not settings.admin_username or not settings.admin_password_hash:
        pytest.skip("Admin credentials not configured in .env")
    password = os.getenv("TEST_ADMIN_PASSWORD")
    if not password:
        pytest.skip("TEST_ADMIN_PASSWORD not set for integration tests")
    return settings.admin_username, password

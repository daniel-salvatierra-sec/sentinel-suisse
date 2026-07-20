"""Freemium entitlement unit tests."""

from types import SimpleNamespace

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.services.entitlements import (
    EntitlementError,
    assert_can_use_whatsapp,
    max_saved_searches,
)


def test_max_saved_searches_free_vs_premium() -> None:
    settings = Settings(free_max_saved_searches=1, premium_max_saved_searches=5)
    free = SimpleNamespace(is_premium=False)
    premium = SimpleNamespace(is_premium=True)
    assert max_saved_searches(free, settings) == 1  # type: ignore[arg-type]
    assert max_saved_searches(premium, settings) == 5  # type: ignore[arg-type]


def test_whatsapp_requires_premium() -> None:
    free = SimpleNamespace(is_premium=False)
    premium = SimpleNamespace(is_premium=True)
    with pytest.raises(EntitlementError) as exc:
        assert_can_use_whatsapp(free)  # type: ignore[arg-type]
    assert exc.value.code == "whatsapp_requires_premium"
    assert_can_use_whatsapp(premium)  # type: ignore[arg-type]

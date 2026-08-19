"""Freemium entitlement unit tests."""

from types import SimpleNamespace

import pytest

from sentinel_suisse.config import Settings
from sentinel_suisse.services.entitlements import (
    EntitlementError,
    assert_can_use_whatsapp,
    can_receive_alerts,
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


def test_can_receive_alerts_gates_new_free_signups() -> None:
    premium = SimpleNamespace(is_premium=True, free_alerts_grandfathered=False)
    grandfathered_free = SimpleNamespace(is_premium=False, free_alerts_grandfathered=True)
    new_free = SimpleNamespace(is_premium=False, free_alerts_grandfathered=False)

    assert can_receive_alerts(premium) is True  # type: ignore[arg-type]
    assert can_receive_alerts(grandfathered_free) is True  # type: ignore[arg-type]
    assert can_receive_alerts(new_free) is False  # type: ignore[arg-type]

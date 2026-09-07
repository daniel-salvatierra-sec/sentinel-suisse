"""Watchdog status classification (no network)."""

import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path

_WATCHDOG = Path(__file__).resolve().parents[1] / "deploy" / "watchdog.py"
_SPEC = importlib.util.spec_from_file_location("linkswiss_watchdog", _WATCHDOG)
assert _SPEC and _SPEC.loader
watchdog = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(watchdog)


def test_parse_health_ok() -> None:
    assert watchdog.parse_health('{"status":"ok","database":"ok"}', 200) == "ok"


def test_parse_health_degraded() -> None:
    assert watchdog.parse_health('{"status":"degraded","database":"error"}', 503) == (
        "health HTTP 503"
    )
    assert watchdog.parse_health('{"status":"degraded","database":"error"}', 200).startswith(
        "health:"
    )


def test_classify_fail_beats_stale() -> None:
    old = datetime.now(UTC) - timedelta(days=5)
    assert watchdog.classify("health HTTP 502", old) == "fail"


def test_classify_stale() -> None:
    old = datetime.now(UTC) - timedelta(hours=80)
    assert watchdog.classify("ok", old) == "stale"


def test_classify_fresh() -> None:
    recent = datetime.now(UTC) - timedelta(hours=2)
    assert watchdog.classify("ok", recent) == "ok"


def test_state_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "watchdog.state"
    watchdog.write_state("fail", path)
    assert watchdog.read_state(path) == "fail"

#!/usr/bin/env python3
"""Host-side LinkSwiss watchdog: health + ingest age → WhatsApp + email.

Runs on the VPS (no Docker rebuild). Cron every 5 minutes.
Alerts only when the status changes (down / stale / recovered).
"""

from __future__ import annotations

import json
import smtplib
import ssl
import subprocess
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
STATE_FILE = ROOT / "var" / "watchdog.state"
HEALTH_URL = "https://linkswiss.ch/health"
STALE_AFTER = timedelta(hours=72)
GRAPH_API = "https://graph.facebook.com/v21.0"


def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def parse_health(body: str, status_code: int) -> str:
    if status_code != 200:
        return f"health HTTP {status_code}"
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return "health: respuesta no JSON"
    if payload.get("status") != "ok" or payload.get("database") != "ok":
        return f"health: {payload}"
    return "ok"


def _https_url(url: str) -> str:
    if not url.startswith("https://"):
        msg = "watchdog only allows https URLs"
        raise ValueError(msg)
    return url


def fetch_health(url: str = HEALTH_URL, timeout: float = 12.0) -> str:
    request = urllib.request.Request(  # noqa: S310
        _https_url(url), headers={"User-Agent": "linkswiss-watchdog"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            body = response.read().decode("utf-8", errors="replace")
            return parse_health(body, response.status)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return parse_health(body, exc.code)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return f"health unreachable: {exc}"


def listing_last_fetch(root: Path = ROOT) -> datetime | None:
    cmd = [
        "docker",
        "compose",
        "-f",
        "docker-compose.prod.yml",
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "sentinel",
        "-d",
        "sentinel_suisse",
        "-tA",
        "-c",
        "SELECT max(fetched_at) FROM listings;",
    ]
    try:
        result = subprocess.run(  # noqa: S603
            cmd,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    raw = " ".join((result.stdout or "").split())
    if result.returncode != 0 or not raw or raw in {"\\N", "null"}:
        return None
    if " " in raw:
        raw = raw.replace(" ", "T", 1)
    if raw.endswith("+00"):
        raw = raw + ":00"
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def classify(health: str, last_fetch: datetime | None, now: datetime | None = None) -> str:
    if health != "ok":
        return "fail"
    if last_fetch is None:
        return "ok"
    when = now or datetime.now(UTC)
    fetched = last_fetch if last_fetch.tzinfo else last_fetch.replace(tzinfo=UTC)
    if when - fetched > STALE_AFTER:
        return "stale"
    return "ok"


def read_state(path: Path = STATE_FILE) -> str:
    if not path.is_file():
        return "ok"
    return path.read_text(encoding="utf-8").strip().splitlines()[0] if path.stat().st_size else "ok"


def write_state(status: str, path: Path = STATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(status + "\n", encoding="utf-8")


def send_email(env: dict[str, str], subject: str, body: str) -> None:
    to_addr = env.get("OPS_ALERT_EMAIL", "").strip()
    host = env.get("SMTP_HOST", "").strip()
    from_addr = env.get("SMTP_FROM", "").strip()
    if not (to_addr and host and from_addr):
        return
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_addr
    message["To"] = to_addr
    message.set_content(body)
    port = int(env.get("SMTP_PORT") or "587")
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if env.get("SMTP_USE_TLS", "true").lower() != "false":
            smtp.starttls(context=ssl.create_default_context())
        user = env.get("SMTP_USER", "").strip()
        if user:
            smtp.login(user, env.get("SMTP_PASSWORD", ""))
        smtp.send_message(message)


def send_whatsapp(env: dict[str, str], text: str) -> None:
    token = env.get("WHATSAPP_TOKEN", "").strip()
    phone_id = env.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    to_phone = "".join(ch for ch in env.get("OPS_ALERT_WHATSAPP", "") if ch.isdigit())
    if not (token and phone_id and to_phone):
        return
    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"body": text},
        }
    ).encode("utf-8")
    safe_id = "".join(ch for ch in phone_id if ch.isdigit())
    request = urllib.request.Request(  # noqa: S310
        _https_url(f"{GRAPH_API}/{safe_id}/messages"),
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310
        response.read()


def notify(env: dict[str, str], status: str, detail: str) -> None:
    if status == "ok":
        subject = "LinkSwiss: ya está bien"
        text = "LinkSwiss volvió a responder bien.\n" + detail
    elif status == "stale":
        subject = "LinkSwiss: ingest parado"
        text = "LinkSwiss está arriba, pero los anuncios no se actualizan.\n" + detail
    else:
        subject = "LinkSwiss: caída"
        text = "LinkSwiss no responde bien.\n" + detail
    errors: list[str] = []
    try:
        send_email(env, subject, text)
    except (OSError, smtplib.SMTPException) as exc:
        errors.append(f"email: {exc}")
    try:
        send_whatsapp(env, text)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        errors.append(f"whatsapp: {exc}")
    if errors:
        print("notify partial:", "; ".join(errors))


def main() -> int:
    env = load_env()
    health = fetch_health(env.get("OPS_HEALTH_URL") or HEALTH_URL)
    last_fetch = listing_last_fetch()
    status = classify(health, last_fetch)
    fetched_s = last_fetch.isoformat() if last_fetch else "unknown"
    detail = f"health={health}\nlast_fetch={fetched_s}\n"
    previous = read_state()
    print(f"status={status} previous={previous} {detail.strip()}")
    if status != previous:
        notify(env, status, detail)
        write_state(status)
    return 0 if status != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())

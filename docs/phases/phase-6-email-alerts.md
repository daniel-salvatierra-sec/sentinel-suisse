# Phase 6 — Real email alerts (SMTP)

**Branch:** `feature/phase-6-email-alerts`  
**Goal:** Send listing alerts by email when SMTP is configured; fall back to console otherwise.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-6-email-alerts
pip install -e .
```

### Step 2 — Configure SMTP in `.env`

For development, [Mailtrap](https://mailtrap.io/) is recommended (free sandbox).

```
NOTIFIER_MODE=auto
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=your_mailtrap_user
SMTP_PASSWORD=your_mailtrap_password
SMTP_FROM=alerts@sentinel-suisse.local
SMTP_USE_TLS=true
```

`NOTIFIER_MODE` values:

| Value | Behaviour |
|-------|-----------|
| `auto` | SMTP for email channels when configured; else console |
| `console` | Always log to terminal (Phase 5 behaviour) |
| `smtp` | Require SMTP; fail if missing |

### Step 3 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Admin password"
pytest -v tests/test_email_notifier.py
```

### Step 4 — Dispatch (uses SMTP if configured)

Ensure uvicorn is running and you have user + verified email channel + saved search (Phase 5).

```powershell
python -m sentinel_suisse.alerts --listing-id 1
```

Check your Mailtrap inbox for the email.

### Step 5 — Security + commit

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: Phase 6 SMTP email alerts"
git checkout main
git merge feature/phase-6-email-alerts
git push origin main
```

---

## Security checklist

| # | Check |
|---|-------|
| 1 | SMTP credentials only in `.env` |
| 2 | No email body stored in `alerts_log` |
| 3 | `NOTIFIER_MODE=console` safe default for CI |
| 4 | TLS enabled by default (`SMTP_USE_TLS`) |
| 5 | bandit + pre-commit pass |

---

## Next phase

**Phase 7 — WhatsApp Cloud API** (optional): Meta Business API + webhook verification.

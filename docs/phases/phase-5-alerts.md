# Phase 5 — Alerts pipeline (IN PROGRESS)

**Branch:** `feature/phase-5-alerts`  
**Goal:** Match new listings to saved searches and dispatch alerts (pilot: console log + `alerts_log`).

---

## Your steps (run in order)

### Step 1 — Branch + migration

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-5-alerts
pip install -r requirements.txt
pip install -e .
alembic upgrade head
```

### Step 2 — Register + verify notification channel

Use your existing user API key (`$plainKey`).

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/notification-channels" -Headers @{ "X-API-Key" = $plainKey } -ContentType "application/json" -Body '{"channel_type":"email","channel_address":"you@example.com","is_primary":true}'
```

Note the `id` from the response. Admin verifies it (replace `CHANNEL_ID`):

```powershell
$pass = Read-Host "Admin password" -AsSecureString
```

(Then base64 steps as in Phase 4, one command at a time.)

Or use Swagger: `PATCH /api/v1/notification-channels/{id}/verify` with admin auth.

### Step 3 — Dispatch alert (CLI pilot)

```powershell
python -m sentinel_suisse.alerts --listing-id 1
```

**Expected:** `matched=1 sent=1` and a log line with Geneva listing.

Run again:

**Expected:** `skipped=1` (dedup).

### Step 4 — Verify `alerts_log`

```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U sentinel -d sentinel_suisse -h 127.0.0.1 -c "SELECT id, listing_id, status, channel_type FROM alerts_log;"
```

### Step 5 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Admin password"
pytest -v
```

### Step 6 — Security + commit

```powershell
pre-commit run --all-files
```

```powershell
git add -A
```

```powershell
git commit -m "feat: Phase 5 alert dispatch with console pilot"
```

---

## Security checklist

| # | Check |
|---|-------|
| 1 | No PII in `alerts_log` message body |
| 2 | Dedup: unique `(user, saved_search, listing)` |
| 3 | Channels verified by admin only |
| 4 | User sees only own alerts + channels |
| 5 | Pilot notifier logs only — no external API yet |
| 6 | bandit + pre-commit pass |

---

## New endpoints

| Method | Path | Auth |
|--------|------|------|
| GET/POST | `/api/v1/notification-channels` | `X-API-Key` |
| PATCH | `/api/v1/notification-channels/{id}/verify` | Admin |
| GET | `/api/v1/alerts` | `X-API-Key` |
| POST | `/api/v1/alerts/dispatch?listing_id=` | Admin |
| CLI | `python -m sentinel_suisse.alerts --listing-id N` | Local |

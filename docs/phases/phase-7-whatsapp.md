# Phase 7 — WhatsApp alerts + auto-dispatch on ingest (IN PROGRESS)

**Branch:** `feature/phase-7-whatsapp`  
**Goal:** Send alerts via WhatsApp Cloud API; optionally dispatch after ingest.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-7-whatsapp
pip install -e .
```

### Step 2 — Meta WhatsApp setup (optional for real send)

1. [Meta for Developers](https://developers.facebook.com/) → create app → **WhatsApp** product
2. **API Setup** → copy **Phone number ID** and **temporary access token**
3. Add your phone as test recipient in the Meta dashboard
4. Add to `.env`:

```
WHATSAPP_TOKEN=your_temporary_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
NOTIFIER_MODE=auto
```

Without Meta credentials, WhatsApp channels fall back to **console** (safe for dev).

### Step 3 — User WhatsApp channel

Register channel with API key (`channel_type`: `whatsapp`, `channel_address`: E.164 e.g. `41791234567`).

Admin verifies: `PATCH /api/v1/notification-channels/{id}/verify`

### Step 4 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Admin password"
pytest -v tests/test_whatsapp_notifier.py
```

### Step 5 — Auto-dispatch on ingest (pilot)

Delete a fixture listing to allow re-create, or use a new fixture entry:

```powershell
python -m sentinel_suisse.ingest --provider homegate --fixture fixtures/homegate_sample.json --dispatch-alerts
```

With `created=0` (dedup), no new alerts. To test: remove one listing from DB or change `external_id` in fixture temporarily.

Or set in `.env`:

```
INGEST_DISPATCH_ALERTS=true
```

### Step 6 — Commit

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: Phase 7 WhatsApp alerts and ingest auto-dispatch"
git checkout main
git merge feature/phase-7-whatsapp
git push origin main
```

---

## Security checklist

| # | Check |
|---|-------|
| 1 | `WHATSAPP_TOKEN` only in `.env` |
| 2 | Phone numbers treated as PII (`channel_address`) |
| 3 | No message body in `alerts_log` |
| 4 | Graph API over HTTPS only |
| 5 | Console fallback when WhatsApp not configured |
| 6 | bandit + pre-commit pass |

---

## New behaviour

| Feature | Detail |
|---------|--------|
| `WhatsAppNotifier` | Meta Graph API `v21.0` text messages |
| Factory | `whatsapp` channel → API when configured |
| Ingest | `--dispatch-alerts` or `INGEST_DISPATCH_ALERTS=true` |

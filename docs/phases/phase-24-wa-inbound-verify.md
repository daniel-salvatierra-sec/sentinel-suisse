# Phase 24 — WhatsApp inbound auto-verify

**Branch:** `feature/phase-24-wa-inbound-verify`  
**Goal:** When Meta posts an inbound WhatsApp message, mark matching unverified channels as verified (phone control proof).

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-24-wa-inbound-verify
pip install -e .
```

### Step 2 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect previous suite + new extract / auto-verify tests (**~73+ passed**).

### Step 3 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: auto-verify WhatsApp channels from inbound webhook (Phase 24)"
git checkout main
git merge feature/phase-24-wa-inbound-verify
git push origin main
```

---

## Behaviour

1. User signs up with WhatsApp number (unverified if `SIGNUP_AUTO_VERIFY=false`)
2. User sends any message to the Meta business number
3. Meta `POST /api/v1/webhooks/whatsapp` with `messages[].from`
4. Sentinel decrypts unverified WhatsApp channels, matches digits-only phone, sets `is_verified=true`

Toggle: `WHATSAPP_INBOUND_AUTO_VERIFY=true` (default).

## Security

| Check | Notes |
|-------|--------|
| Signature | Still enforced when `WHATSAPP_APP_SECRET` set |
| Phone match | Only channels already registered for that user phone |
| Logs | No raw phone numbers in webhook log lines |
| PII | Decrypt at rest for match only |

## Out of scope (Phase 25+)

- Hosting / TLS
- Keyword-gated verify (e.g. only "OK")
- Full conversational bot

# Phase 23 — Production signup flag + WhatsApp webhook scaffold

**Branch:** `feature/phase-23-webhook-signup`  
**Goal:** Enable public signup via `PUBLIC_SIGNUP_ENABLED` (works outside development) and add Meta WhatsApp webhook verify/receive endpoints ready for hosting/tunnel.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-23-webhook-signup
pip install -e .
```

### Step 2 — Local webhook smoke test (API running)

```powershell
# In .env for this test only (do not commit secrets):
# WHATSAPP_VERIFY_TOKEN=dev-local-token
```

Restart uvicorn, then:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=dev-local-token&hub.challenge=abc123"
```

Expected: plain text `abc123`.

### Step 3 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **~71 passed** (previous 63 + webhook/signup flag tests).

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: public signup flag and WhatsApp webhook scaffold (Phase 23)"
git checkout main
git merge feature/phase-23-webhook-signup
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Config | `PUBLIC_SIGNUP_ENABLED`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET` |
| Signup | `_require_public_signup()` — auto on in development; force with flag in production |
| Search | Still development-only (`_require_public_preview`) |
| Webhook | `GET/POST /api/v1/webhooks/whatsapp` |
| Security | HMAC `X-Hub-Signature-256` when app secret set; PII-safe log summary |
| CORS | Allows `PUBLIC_APP_URL` origin |
| API version | `0.23.0` |

## Production notes (when you pick hosting)

1. Set `PUBLIC_APP_URL=https://your-domain`
2. Set `PUBLIC_SIGNUP_ENABLED=true` and `SIGNUP_AUTO_VERIFY=false`
3. Point Meta webhook to `https://your-domain/api/v1/webhooks/whatsapp`
4. Set `WHATSAPP_VERIFY_TOKEN` + `WHATSAPP_APP_SECRET` from Meta app settings
5. Local tunnel (ngrok/cloudflared) works the same for testing

## Out of scope (Phase 24+)

- Hosting / TLS termination itself
- Parsing inbound WhatsApp to auto-verify channels
- Full Meta conversation flows / templates beyond alerts

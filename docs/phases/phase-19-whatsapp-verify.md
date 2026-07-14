# Phase 19 — WhatsApp channel verification

**Branch:** `feature/phase-19-whatsapp-verify`  
**Goal:** Send WhatsApp verification links on signup; unified `verify-channel` endpoint; UX improvements for signup and alerts.

---

## UX changes (same phase)

| Change | Detail |
|--------|--------|
| Signup in **Compte** | Registration form moved from Alertes tab |
| **Alertes** tab | Shows saved preferences when logged in; links to Compte if not |
| Country code picker | Searchable dial code by country name (5 langs) |
| Map center | Follows search query (e.g. Geneva) not only first listing |

Browser test: **Compte** → sign up with country picker → **Alertes** → see preferences (no duplicate signup form).

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-19-whatsapp-verify
pip install -e .
```

### Step 2 — Test flow (dev)

In API terminal:

```powershell
$env:SIGNUP_AUTO_VERIFY = "false"
$env:NOTIFIER_MODE = "console"
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000 --reload
```

1. Open **Compte** tab → sign up with email and optional WhatsApp (country picker)
2. Logs show `VERIFICATION EMAIL` and `VERIFICATION WHATSAPP` URLs
3. Open either link → channel verified (banner shows email or WhatsApp message)
4. **Alertes** tab → shows your saved preferences (not signup form again)

### Step 3 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **56 passed**.

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add WhatsApp channel verification (Phase 19)"
git checkout main
git merge feature/phase-19-whatsapp-verify
git push origin main
```

---

## API

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/api/v1/public/verify-channel?token=` | Email or WhatsApp |
| `GET` | `/api/v1/public/verify-email?token=` | Alias (backward compatible) |

Signup response adds `whatsapp_verification_sent: bool`.

---

## Out of scope (Phase 20+)

- Meta webhook inbound verification
- QR code scan-to-subscribe
- Additional portals (Flatfox, ImmoScout)
- Production public signup

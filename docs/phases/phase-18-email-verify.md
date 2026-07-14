# Phase 18 — Email verification (production signup)

**Branch:** `feature/phase-18-email-verify`  
**Goal:** Signed verification links for email channels when auto-verify is disabled.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-18-email-verify
pip install -e .
```

### Step 2 — Test verification flow in dev

Add to `.env` (temporary test):

```
SIGNUP_AUTO_VERIFY=false
SECRET_KEY=your-long-random-secret-here
PUBLIC_APP_URL=http://127.0.0.1:5173
```

Restart uvicorn + `npm run dev`.

1. Sign up via **Alertes** tab
2. Check uvicorn logs for `VERIFICATION EMAIL ... url=http://127.0.0.1:5173/?verify=...`
3. Open that URL in the browser → green banner “E-mail confirmé”
4. Tab **Compte** → channel should be verified

Remove `SIGNUP_AUTO_VERIFY=false` when done testing (dev defaults to auto-verify).

### Step 3 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **55 passed** (4 new verification tests).

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add email verification links for signup (Phase 18)"
git checkout main
git merge feature/phase-18-email-verify
git push origin main
```

---

## API

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| `GET` | `/api/v1/public/verify-email?token=` | None | All environments |
| `POST` | `/api/v1/public/signup` | None | Sends email when `SIGNUP_AUTO_VERIFY=false` |

## Config

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | — | HMAC token signing (required for verify) |
| `PUBLIC_APP_URL` | `http://127.0.0.1:5173` | Link target in verification email |
| `SIGNUP_AUTO_VERIFY` | auto | `false` forces verification email even in dev |
| `VERIFICATION_TOKEN_TTL_HOURS` | `48` | Link expiry |

Without SMTP, verification URL is logged to stdout (same as console notifier pattern).

---

## Out of scope (Phase 20+)

- WhatsApp QR onboarding
- Additional portals
- Production public signup (`APP_ENV=production`)

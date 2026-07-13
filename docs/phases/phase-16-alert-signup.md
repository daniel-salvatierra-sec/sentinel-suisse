# Phase 16 — Public alert signup (wire UI to backend)

**Branch:** `feature/phase-16-alert-signup`  
**Goal:** Connect Suisse Alert signup to user + channels + saved search API.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-16-alert-signup
pip install -e .
```

### Step 2 — Start API + UI (two terminals)

**Terminal 1:**
```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2:**
```powershell
cd C:\Users\danin\Projects\sentinel-suisse\frontend
npm run dev
```

### Step 3 — Test signup in browser

1. Open **http://127.0.0.1:5173**
2. Tab **Alertes**
3. Enter email, optional WhatsApp, check privacy consent
4. Click **Activer l'alerte**
5. Expect success message; `api_key` stored in `localStorage` (`suisse-alert-api-key`)

### Step 4 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **49 passed** (4 new signup tests).

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: wire public alert signup to backend (Phase 16)"
git checkout main
git merge feature/phase-16-alert-signup
git push origin main
```

---

## API

`POST /api/v1/public/signup` — **development only** (`APP_ENV=development`)

```json
{
  "email": "you@example.com",
  "phone": "+41791234567",
  "locale": "fr",
  "consent": true,
  "query": { "listing_type": "housing", "location": "Geneva" }
}
```

Response (api_key shown once):

```json
{
  "api_key": "...",
  "user_id": 1,
  "saved_search_id": 1,
  "email_verified": true,
  "whatsapp_verified": true,
  "verification_pending": false
}
```

In development, email and WhatsApp channels are **auto-verified** so alerts can dispatch immediately.

---

## Security notes

- Rate limit: **5/minute** on signup
- Email required (user account); WhatsApp optional
- Privacy consent checkbox required
- PII encrypted at rest (Fernet)
- Production returns **404** until public launch review

---

## Out of scope (Phase 17+)

- Email confirmation links (production verify flow)
- Real WhatsApp QR onboarding
- Additional housing/job portals
- Account management UI

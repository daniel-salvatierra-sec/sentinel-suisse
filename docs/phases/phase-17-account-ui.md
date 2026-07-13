# Phase 17 — Account management UI

**Branch:** `feature/phase-17-account-ui`  
**Goal:** Let subscribers view saved alerts, history, and delete account via stored `api_key`.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-17-account-ui
pip install -e .
```

### Step 2 — Start API + UI

**Terminal 1:**
```powershell
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2:**
```powershell
cd frontend
npm run dev
```

### Step 3 — Browser test

1. Open **http://127.0.0.1:5173**
2. Tab **Alertes** → sign up (or use existing session)
3. Tab **Compte** → see email, saved search, alert history
4. Delete a saved search → list updates
5. Delete account (double-click confirm) → session cleared

### Step 4 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **51 passed** (2 new `test_user_me` tests).

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add account management UI (Phase 17)"
git checkout main
git merge feature/phase-17-account-ui
git push origin main
```

---

## API added

| Method | Path | Auth |
|--------|------|------|
| `GET` | `/api/v1/users/me` | `X-API-Key` |

Existing endpoints used by UI: `GET/DELETE /saved-searches`, `GET /alerts`, `DELETE /users/me`.

---

## Out of scope (Phase 19+)

- WhatsApp QR onboarding
- Additional housing/job portals
- Production public signup without review
- Edit saved search from UI

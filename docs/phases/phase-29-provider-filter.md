# Phase 29 — Provider filter chips (public search)

**Branch:** `feature/phase-29-provider-filter`  
**Goal:** Let users filter listings by portal (Homegate, Flatfox, ImmoScout24, jobs.ch, …) via public chips.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-29-provider-filter
pip install -e .
```

### Step 2 — UI check

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173** — chips under filters (Tous / Homegate / …). Selecting a chip refreshes the list.

### Step 3 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **79 passed**.

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add public provider filter chips (Phase 29)"
git checkout main
git merge feature/phase-29-provider-filter
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| API | `GET /api/v1/public/providers` (active only, same gate as search) |
| API | `provider_id` on `GET /api/v1/public/search` |
| UI | Provider chips in `FilterBar` |
| i18n | `providerFilter`, `allProviders` (5 langs) |
| Versions | `0.29.0` |

## Out of scope (Phase 30+)

- Hosting / TLS
- Infinite scroll
- Multi-select providers

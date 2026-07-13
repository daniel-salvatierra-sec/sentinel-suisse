# Phase 15 — Suisse Alert frontend (mobile-first)

**Branch:** `feature/phase-15-frontend`  
**Goal:** React + Vite UI for housing and jobs — 5 languages, map, guide bot, alert signup preview.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-15-frontend
pip install -e .
```

### Step 2 — Install frontend dependencies

```powershell
cd frontend
npm install
```

### Step 3 — Start API (terminal 1)

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 4 — Start UI (terminal 2)

```powershell
cd C:\Users\danin\Projects\sentinel-suisse\frontend
npm run dev
```

Open **http://127.0.0.1:5173** — pick a language, then browse housing / jobs.

### Step 5 — Fixture data (if search is empty)

```powershell
python -m sentinel_suisse.ingest --provider homegate --fixture fixtures/homegate_sample.json
python -m sentinel_suisse.ingest --provider jobs --fixture fixtures/jobs_sample.json
```

### Step 6 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

### Step 7 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add Suisse Alert mobile-first frontend (Phase 15)"
git checkout main
git merge feature/phase-15-frontend
git push origin main
```

---

## UI features

| Feature | Status |
|---------|--------|
| Language bar (fr, de, es, pt, en) at top | Done |
| Housing / Job category cards | Done |
| Search bar + public API | Done (dev only) |
| Leaflet map with city pins | Done |
| Floating guide bot | Done |
| Alert panel (QR placeholder + WhatsApp/email) | Wired to `POST /api/v1/public/signup` (Phase 16) |
| Swiss palette (lake / mountain / Jet d'Eau) | Done |

## API

- `GET /api/v1/public/search` — unauthenticated, **`APP_ENV=development` only**
- Vite proxies `/api` → `http://127.0.0.1:8000`

## Production build (optional)

```powershell
cd frontend
npm run build
```

With `frontend/dist` present, FastAPI serves the SPA at `/` (API routes take precedence).

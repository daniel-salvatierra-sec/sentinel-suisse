# Phase 4 — Search API + saved searches (IN PROGRESS)

**Branch:** `feature/phase-4-search`  
**Goal:** Filter listings, let users save searches with API keys, enforce per-user isolation.

---

## Your steps (run in order)

### Step 1 — Branch + migration

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-4-search
pip install -r requirements.txt
pip install -e .
alembic upgrade head
```

### Step 2 — Start API

```powershell
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **http://127.0.0.1:8000/docs**

### Step 3 — Create a user (admin auth)

`POST /api/v1/users` with admin HTTP Basic:

```json
{"email": "you@example.com", "is_active": true}
```

**Save the `api_key` from the response** — shown only once.

### Step 4 — Search listings

`GET /api/v1/search?location=Geneva&listing_type=housing`

Auth: **either** admin HTTP Basic **or** header `X-API-Key: <api_key>`.

Expected: 1 listing (`hg-demo-001`).

### Step 5 — Saved search

`POST /api/v1/saved-searches` with header `X-API-Key`:

```json
{
  "name": "Geneva housing",
  "query": {"location": "Geneva", "listing_type": "housing"},
  "is_active": true
}
```

Expected: **201 Created**.

### Step 6 — Isolation tests

Set your admin password for tests (session only — do not commit):

```powershell
$env:TEST_ADMIN_PASSWORD = "your-admin-password"
pytest -v
```

Expected: tests pass (user B cannot read user A's saved search).

### Step 7 — Security checks

```powershell
bandit -c pyproject.toml -r src
pre-commit run --all-files
```

### Step 8 — Commit

```powershell
git add -A
git commit -m "feat: Phase 4 search API and user saved searches"
git checkout main
git merge feature/phase-4-search
git push origin main
```

---

## Security checklist

| # | Check |
|---|-------|
| 1 | API keys stored as bcrypt hash only |
| 2 | `api_key` returned once on create/regenerate |
| 3 | Saved searches scoped by `user_id` — 404 for other users |
| 4 | Search filters validated via Pydantic (`SearchQuery`) |
| 5 | No raw SQL in search — SQLAlchemy ORM only |
| 6 | Admin routes still require HTTP Basic |
| 7 | bandit + pre-commit pass |

---

## New endpoints

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/search` | Admin or `X-API-Key` |
| GET/POST/PATCH | `/api/v1/users` | Admin |
| POST | `/api/v1/users/{id}/regenerate-api-key` | Admin |
| CRUD | `/api/v1/saved-searches` | `X-API-Key` |

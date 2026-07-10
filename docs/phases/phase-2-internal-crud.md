# Phase 2 — Internal CRUD API (COMPLETED)

**Project:** Sentinel Suisse  
**Author:** Daniel Salvatierra  
**Date completed:** 10 July 2026  
**Branch:** `feature/phase-2-internal-crud`  
**Commit:** (add hash after successful commit)

---

## Objective

FastAPI admin CRUD for providers/listings on **localhost only** (`127.0.0.1:8000`).

---

## Evidence

| Test | Result |
|------|--------|
| `GET /health` | 200 OK |
| `POST /api/v1/providers` (with auth) | **201 Created** — Homegate |
| bandit | 0 issues (571 LOC) |
| pre-commit | Passed (after B008 ignore for FastAPI Depends) |
| `.env` not in git | Verified |

---

## Commands executed

```powershell
git checkout -b feature/phase-2-internal-crud
pip install -r requirements.txt
pip install -e .
python scripts/generate_admin_hash.py
# ADMIN_USERNAME + ADMIN_PASSWORD_HASH in .env
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000 --reload
bandit -c pyproject.toml -r src
pre-commit run --all-files
git commit -m "feat: Phase 2 internal CRUD API with admin auth"
git checkout main && git merge feature/phase-2-internal-crud
git push origin main
```

---

## Security checklist (all passed)

| # | Check | Evidence |
|---|-------|----------|
| 1 | bandit clean | 0 medium/high |
| 2 | ORM only (no raw SQL) | routes use `db.get`, `select()` |
| 3 | Pydantic validation | `schemas/` |
| 4 | Admin auth on CRUD | 401 without login, 201 with login |
| 5 | Rate limiting | slowapi on routes |
| 6 | Localhost bind | `--host 127.0.0.1` |
| 7 | Password as bcrypt hash only | `.env` hash, not plaintext |
| 8 | gitleaks | Passed |

---

## Note: pre-commit blocked first commit (expected)

Ruff rule `B008` flags `Depends()` in FastAPI defaults — false positive. Fixed via `per-file-ignores` in `pyproject.toml` for `src/sentinel_suisse/api/**`.

---

## Next phase

**Phase 3 — Ingestion pipeline:** fetch listings from external portals (Homegate pilot), dedup, rate limits.

**Project:** Sentinel Suisse  
**Branch:** `feature/phase-2-internal-crud`  
**Goal:** FastAPI admin CRUD for providers/listings on **localhost only**.

---

## What was added

| Component | Path |
|-----------|------|
| FastAPI app | `src/sentinel_suisse/main.py` |
| Admin auth (bcrypt) | `src/sentinel_suisse/api/auth.py` |
| Rate limiting | `src/sentinel_suisse/api/rate_limit.py` |
| Provider CRUD | `src/sentinel_suisse/api/routes/providers.py` |
| Listing CRUD | `src/sentinel_suisse/api/routes/listings.py` |
| Pydantic schemas | `src/sentinel_suisse/schemas/` |
| Password hash helper | `scripts/generate_admin_hash.py` |

---

## Your steps (run in order)

### Step 1 — New branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-2-internal-crud
```

### Step 2 — Install new dependencies

```powershell
pip install -r requirements.txt
pip install -e .
```

### Step 3 — Configure admin credentials (never commit password)

```powershell
python scripts/generate_admin_hash.py
```

Copy output into `.env`:

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<paste hash here>
```

### Step 4 — Start API (localhost only)

```powershell
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected:** `Uvicorn running on http://127.0.0.1:8000`

### Step 5 — Test health (no auth)

Open browser: **http://127.0.0.1:8000/health**

**Expected:** `{"status":"ok","env":"development"}`

### Step 6 — Test provider CRUD (with auth)

Open **http://127.0.0.1:8000/docs** → Authorize with your admin user/password.

Or PowerShell:

```powershell
$cred = "admin:YOUR_PASSWORD"
$encoded = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($cred))
$headers = @{ Authorization = "Basic $encoded" }

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/providers" -Headers $headers

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/providers" -Method POST -Headers $headers -ContentType "application/json" -Body '{"name":"Homegate","slug":"homegate","base_url":"https://www.homegate.ch","is_active":true}'
```

### Step 7 — Security checks

```powershell
bandit -c pyproject.toml -r src
pre-commit run --all-files
```

### Step 8 — Commit and merge

```powershell
git add -A
git status
git commit -m "feat: Phase 2 internal CRUD API with admin auth"
git checkout main
git merge feature/phase-2-internal-crud
git push origin main
```

---

## Phase 2 security checklist

| # | Check | How |
|---|-------|-----|
| 1 | bandit no medium/high | `bandit -r src` |
| 2 | No raw SQL | Code review routes |
| 3 | Pydantic on all inputs | schemas/ folder |
| 4 | Admin auth on CRUD routes | Test without auth → 401 |
| 5 | Rate limiting active | `slowapi` on routes |
| 6 | Server binds 127.0.0.1 only | uvicorn `--host 127.0.0.1` |
| 7 | No password in git | `gitleaks` + `.env` ignored |
| 8 | pre-commit passes | `pre-commit run --all-files` |

---

## Completion

Update this file with commit hash, test output, and date when Phase 2 is closed.

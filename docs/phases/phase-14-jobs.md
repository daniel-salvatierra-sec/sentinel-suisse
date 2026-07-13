# Phase 14 — jobs.ch connector (employment)

**Branch:** `feature/phase-14-jobs`  
**Goal:** Ingest Swiss job vacancies from jobs.ch; `listing_type=job`; live **disabled by default**.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-14-jobs
pip install -e .
```

### Step 2 — Register jobs.ch provider (once)

With uvicorn running and admin auth:

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/providers" -Authentication Basic -Credential (New-Object PSCredential("admin", (ConvertTo-SecureString $pass -AsPlainText -Force))) -ContentType "application/json" -Body '{"name":"jobs.ch","slug":"jobs","base_url":"https://www.jobs.ch","is_active":true}'
```

### Step 3 — Fixture ingest

```powershell
python -m sentinel_suisse.ingest --provider jobs --fixture fixtures/jobs_sample.json
```

Expected: `created=2` (first run).

### Step 4 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **43 passed**.

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add jobs.ch connector with job listing type"
git checkout main
git merge feature/phase-14-jobs
git push origin main
```

---

## Mixed housing + job search

Saved searches already support `listing_type` in query JSON:

```json
{"location": "Geneva", "listing_type": "job"}
```

Alerts will only match job listings from the `jobs` provider.

---

## UI note

Backend only in this phase. Frontend / presentation model comes in a later phase after you pick visual references.

# Phase 3 — Ingestion pipeline (IN PROGRESS)

**Branch:** `feature/phase-3-ingestion`  
**Goal:** Load listings into PostgreSQL with deduplication. Pilot uses a **JSON fixture** (legal, controlled) before any live scraping.

---

## Your steps (run in order)

### Step 1 — Branch + dependencies

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-3-ingestion
```

Ensure `.env` uses:

```
DATABASE_URL=postgresql://sentinel:sentinel@127.0.0.1:5432/sentinel_suisse
```

```powershell
pip install -r requirements.txt
pip install -e .
```

### Step 2 — Run pilot ingest (fixture)

```powershell
python -m sentinel_suisse.ingest --provider homegate --fixture fixtures/homegate_sample.json
```

**Expected:**

```
Ingest complete for provider='homegate'
  created=2 updated=0 skipped=0
```

Run again — second time:

```
  created=0 updated=0 skipped=2
```

(Idempotent — dedup works.)

### Step 3 — Verify in database

```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U sentinel -d sentinel_suisse -h 127.0.0.1 -c "SELECT id, external_id, title, price FROM listings;"
```

### Step 4 — Security checks

```powershell
bandit -c pyproject.toml -r src
pre-commit run --all-files
```

### Step 5 — Commit

```powershell
git add -A
git commit -m "feat: Phase 3 ingestion pipeline with fixture pilot"
git checkout main
git merge feature/phase-3-ingestion
git push origin main
```

---

## Security checklist

| # | Check |
|---|-------|
| 1 | No credentials in fixture or logs |
| 2 | ORM upsert only (no raw SQL) |
| 3 | Pydantic validates fixture JSON |
| 4 | Dedup: second run skips unchanged rows |
| 5 | Legal review documented before live scrape |
| 6 | bandit + pre-commit pass |

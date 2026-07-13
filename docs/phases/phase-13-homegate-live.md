# Phase 13 — Homegate live connector (opt-in)

**Branch:** `feature/phase-13-homegate-live`  
**Goal:** Parse Homegate search results from embedded JSON; live fetch **disabled by default**.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-13-homegate-live
pip install -e .
```

### Step 2 — Tests (no network)

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **40 passed**.

### Step 3 — Fixture ingest still works

```powershell
python -m sentinel_suisse.ingest --provider homegate --fixture fixtures/homegate_sample.json
```

### Step 4 — Live ingest (optional, after legal review)

Add to `.env`:

```
INGEST_HOMEGATE_LIVE=true
```

```powershell
python -m sentinel_suisse.ingest --provider homegate --live
```

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add opt-in Homegate live search connector"
git checkout main
git merge feature/phase-13-homegate-live
git push origin main
```

---

## What changed

| Item | Detail |
|------|--------|
| Connector | `ingest/connectors/homegate.py` |
| CLI | `--fixture` XOR `--live` |
| Config | `INGEST_HOMEGATE_LIVE`, rate limit, search URL |
| Tests | Parser fixtures, no live HTTP in CI |

---

## Legal note

Homegate has **no public API**. Live mode is off by default. Review ToS and `robots.txt` before production use.

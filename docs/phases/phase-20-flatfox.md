# Phase 20 — Flatfox connector (housing)

**Branch:** `feature/phase-20-flatfox`  
**Goal:** Ingest Swiss rental listings from Flatfox; `listing_type=housing`; live **disabled by default**.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-20-flatfox
pip install -e .
```

### Step 2 — Register Flatfox provider (once)

With uvicorn running and admin auth:

```powershell
$pass = Read-Host "Contraseña admin" -AsSecureString
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/providers" -Authentication Basic -Credential (New-Object PSCredential("admin", $pass)) -ContentType "application/json" -Body '{"name":"Flatfox","slug":"flatfox","base_url":"https://flatfox.ch","is_active":true}'
```

### Step 3 — Fixture ingest

```powershell
python -m sentinel_suisse.ingest --provider flatfox --fixture fixtures/flatfox_sample.json
```

Expected: `created=2` (first run).

### Step 4 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **53 passed** (3 new Flatfox tests).

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add Flatfox connector with housing listings (Phase 20)"
git checkout main
git merge feature/phase-20-flatfox
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Connector | `src/sentinel_suisse/ingest/connectors/flatfox.py` |
| Fixtures | `fixtures/flatfox_sample.json`, `fixtures/flatfox_initial_state.json` |
| CLI | `--provider flatfox` in ingest |
| Config | `INGEST_FLATFOX_LIVE`, `FLATFOX_SEARCH_URL` |
| Tests | `tests/test_flatfox_connector.py` |
| Docs | `docs/providers/flatfox.md` |
| API version | `0.20.0` |

## Out of scope (Phase 21+)

- ImmoScout connector
- Meta WhatsApp webhook
- QR scan-to-subscribe
- Public signup in production

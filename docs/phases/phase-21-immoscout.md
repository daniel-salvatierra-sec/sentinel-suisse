# Phase 21 — ImmoScout24 connector (housing)

**Branch:** `feature/phase-21-immoscout`  
**Goal:** Ingest Swiss rental listings from ImmoScout24.ch; `listing_type=housing`; live **disabled by default**.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-21-immoscout
pip install -e .
```

### Step 2 — Register ImmoScout24 provider (once)

With uvicorn running and admin auth (PowerShell 5.x Basic header):

```powershell
$pass = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pass)
$plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
$headers = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:$plain")))" }
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/providers" -Headers $headers -ContentType "application/json" -Body '{"name":"ImmoScout24","slug":"immoscout","base_url":"https://www.immoscout24.ch","is_active":true}'
```

### Step 3 — Fixture ingest

```powershell
python -m sentinel_suisse.ingest --provider immoscout --fixture fixtures/immoscout_sample.json
```

Expected: `created=2` (first run).

### Step 4 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **62 passed** (3 new ImmoScout tests; prior suite was 59).

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add ImmoScout24 connector with housing listings (Phase 21)"
git checkout main
git merge feature/phase-21-immoscout
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Connector | `src/sentinel_suisse/ingest/connectors/immoscout.py` |
| Fixtures | `fixtures/immoscout_sample.json`, `fixtures/immoscout_initial_state.json` |
| CLI | `--provider immoscout` in ingest |
| Config | `INGEST_IMMOSCOUT_LIVE`, `IMMOSCOUT_SEARCH_URL` |
| Tests | `tests/test_immoscout_connector.py` |
| Docs | `docs/providers/immoscout.md` |
| API version | `0.21.0` |

## Out of scope (Phase 22+)

- Meta WhatsApp webhook (needs public HTTPS)
- QR scan-to-subscribe
- Public signup in production
- Hosting / TLS termination

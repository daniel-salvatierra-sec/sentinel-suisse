# Phase 27 — Public search in production (opt-in flag)

**Branch:** `feature/phase-27-public-search`  
**Goal:** Allow `GET /api/v1/public/search` outside development via `PUBLIC_SEARCH_ENABLED=true` (same pattern as signup).

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-27-public-search
pip install -e .
```

### Step 2 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **76 passed** (1 new production search flag test).

### Step 3 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add public search production flag (Phase 27)"
git checkout main
git merge feature/phase-27-public-search
git push origin main
```

---

## Behaviour

| `APP_ENV` | `PUBLIC_SEARCH_ENABLED` | Search |
|-----------|-------------------------|--------|
| development | (omit) | On |
| production | omit / false | Off (404) |
| production | true | On |

Signup remains separate (`PUBLIC_SIGNUP_ENABLED`).

## Production checklist (when hosting)

```
APP_ENV=production
PUBLIC_APP_URL=https://your-domain
PUBLIC_SEARCH_ENABLED=true
PUBLIC_SIGNUP_ENABLED=true
SIGNUP_AUTO_VERIFY=false
```

## Out of scope (Phase 28+)

- Hosting / TLS termination itself
- LLM conversational guide
- Pagination / advanced filters on public search

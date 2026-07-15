# Phase 31 — Multi-select provider filter

**Branch:** `feature/phase-31-provider-multiselect`  
**Goal:** Allow selecting several portals at once (chips toggle); API accepts repeated `provider_ids`.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-31-provider-multiselect
```

### Step 2 — UI check

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173** (API on `:8000`). On the filter chips:

1. **Tous / All** = no portal filter (all providers).
2. Click two portals → both stay active; results only from those two.
3. Click an active portal again → toggles off.
4. Click **Tous** → clears selection.

### Step 3 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$secure = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$env:TEST_ADMIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
pytest -q
```

Expect **79+ passed** (multi provider filter covered in `test_public_preview.py`).

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: multi-select provider filter chips (Phase 31)"
git checkout main
git merge feature/phase-31-provider-multiselect
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Schema | `SearchQuery.provider_ids` + `resolved_provider_ids()` (keeps legacy `provider_id`) |
| API | `GET /public/search` and `/search` accept repeated `provider_ids` |
| UI | Chips multi-toggle; empty selection = all |
| Tests | Multi + combined with legacy `provider_id` |
| Versions | `0.31.0` |

## Out of scope (later)

- Hosting / TLS
- Virtualized long lists

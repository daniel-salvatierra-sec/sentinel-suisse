# Phase 30 — Infinite scroll on listing list

**Branch:** `feature/phase-30-infinite-scroll`  
**Goal:** Auto-load the next page when the user scrolls near the bottom of the list (IntersectionObserver); replace the “Load more” button.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-30-infinite-scroll
```

### Step 2 — UI check

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173** (API on `:8000`). On **Liste**, scroll down: more results should load; when done, “Fin des résultats” / equivalent.

Tip: if you have few fixtures, lower awareness — page size is still 20; ingest more fixtures or check with many providers.

### Step 3 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$secure = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$env:TEST_ADMIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
pytest -q
```

Expect **79 passed** (frontend-only phase).

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add infinite scroll on listing list (Phase 30)"
git checkout main
git merge feature/phase-30-infinite-scroll
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| UI | `InfiniteScrollSentinel.tsx` + list footer |
| i18n | `endOfResults` (5 langs) |
| Removed | Manual “Load more” button |
| Versions | `0.30.0` |

## Out of scope (later)

- Hosting / TLS
- Virtualized long lists (react-window)

(Multi-select providers → Phase 31)

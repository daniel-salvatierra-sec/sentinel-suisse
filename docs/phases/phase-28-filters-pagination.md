# Phase 28 — Advanced filters + pagination (public search UI)

**Branch:** `feature/phase-28-filters-pagination`  
**Goal:** Wire housing price min/max filters and “load more” pagination on the Suisse Alert UI (API already supported `price_*`, `limit`, `offset`).

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-28-filters-pagination
```

### Step 2 — UI check

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173** (API on `:8000`):
1. Category **Logement** → price min/max + Apply
2. List → **Voir plus** when there are enough fixtures (page size 20)

### Step 3 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **77 passed**.

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add price filters and load-more pagination (Phase 28)"
git checkout main
git merge feature/phase-28-filters-pagination
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| API client | `searchListings` sends `price_min`, `price_max`, `limit`, `offset` |
| UI | `FilterBar.tsx` (housing only) + load more on list |
| i18n | `priceMin`, `priceMax`, `applyFilters`, `loadMore` (5 langs) |
| Tests | pagination + price range + invalid range 422 |
| Versions | `0.28.0` |

## Out of scope (Phase 29+)

- Hosting / TLS
- Provider filter chips in UI
- Infinite scroll / virtualized list

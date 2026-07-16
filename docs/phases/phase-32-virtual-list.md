# Phase 32 — Virtualized listing list

**Branch:** `feature/phase-32-virtual-list`  
**Goal:** Only render visible listing cards (+ overscan) with `@tanstack/react-virtual` + window scroll; keep infinite scroll.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-32-virtual-list
```

### Step 2 — Install + UI check

```powershell
cd frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173**. On **Liste**:

1. Scroll — cards load as before (infinite scroll still works).
2. With many results, the DOM should stay light (DevTools → Elements: few `.listing-card` at a time).
3. Click a card → map focus still works.

### Step 3 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$secure = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$env:TEST_ADMIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
pytest -q
```

Expect **79+ passed** (frontend-only phase for UI; backend unchanged).

Optional frontend typecheck:

```powershell
cd frontend
npm run build
```

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: virtualize listing list with tanstack virtual (Phase 32)"
git checkout main
git merge feature/phase-32-virtual-list
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Dep | `@tanstack/react-virtual` |
| UI | `VirtualizedListingList.tsx` + window virtualizer |
| Keep | Infinite scroll sentinel after virtual spacer |
| Versions | `0.32.0` |

## Out of scope (later)

- Hosting / TLS

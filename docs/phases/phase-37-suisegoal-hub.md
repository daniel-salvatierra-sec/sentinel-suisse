# Phase 37 — SuisseGoal hub (Home / Work) + firefly guide

**Branch:** `feature/phase-37-suisegoal-hub`  
**Goal:** Rebrand UI to **SuisseGoal**, vertical Home/Work hub from the Excalidraw sketch, and a firefly companion that opens the guide and animates while searching.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-37-suisegoal-hub
```

### Step 2 — UI check

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173**:

1. Brand shows **SuisseGoal** + tagline (“Tu meta en Suiza” / etc.).
2. Hub: **Home** (top) / **Work** (bottom); active zone expands.
3. Firefly moves toward Home or Work; pulses faster while loading results.
4. Tap firefly → guide opens (avatar ✦).

### Step 3 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$secure = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$env:TEST_ADMIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
pytest -q
```

Expect **85+ passed** (frontend-only phase).

Optional:

```powershell
cd frontend
npm run build
```

### Step 4 — Commit + merge

Run **one command at a time**, top to bottom:

```powershell
pre-commit run --all-files
```

```powershell
git add -A
```

```powershell
git commit -m "feat: SuisseGoal Home Work hub and firefly guide (Phase 37)"
```

```powershell
git checkout main
```

```powershell
git merge feature/phase-37-suisegoal-hub
```

```powershell
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Brand | SuisseGoal + Fraunces display font |
| UI | `GoalHub.tsx` — vertical Home / Work |
| Guide | `FireflyBuddy.tsx` — moves with zone, faster when searching |
| i18n | 5 langs updated |
| Versions | `0.37.0` |

## Out of scope

- Vacaciones zone
- Trademark filing for SuisseGoal
- CV upload for Work

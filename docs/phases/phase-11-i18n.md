# Phase 11 — Five-language i18n (privacy policies)

**Branch:** `feature/phase-11-i18n`  
**Goal:** Extend legal and project i18n to all five mandatory languages: **fr, de, es, pt, en**.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-11-i18n
pip install -e .
```

### Step 2 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **25 passed**.

### Step 3 — Try all languages (uvicorn running)

```powershell
foreach ($lang in @("fr","de","es","pt","en")) {
  Write-Host "--- $lang ---"
  (Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/legal/privacy?lang=$lang").lang
}
```

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: extend privacy policies to five languages (fr de es pt en)"
git checkout main
git merge feature/phase-11-i18n
git push origin main
```

---

## Policy

See [`docs/privacy/i18n.md`](../privacy/i18n.md) — every future user-facing surface ships in all five languages.

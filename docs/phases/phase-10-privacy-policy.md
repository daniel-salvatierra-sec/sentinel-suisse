# Phase 10 — Privacy policy (FR/DE) + public API

**Branch:** `feature/phase-10-privacy-policy`  
**Goal:** Publish nLPD-aligned privacy policies in French and German, served via a public API endpoint.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-10-privacy-policy
pip install -r requirements.txt
pip install -e .
```

### Step 2 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = 'your-admin-plain-password'
pytest -q
```

Expect **22 passed** (4 new privacy policy tests).

### Step 3 — Manual check (optional)

```powershell
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000
```

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/legal/privacy?lang=fr"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/legal/privacy?lang=de"
```

### Step 4 — Before real production

1. Replace `privacy@sentinel-suisse.example` in both policy files with a real contact address.
2. Have policies reviewed by a legal professional (draft status today).

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: publish FR/DE privacy policies via public legal API"
git checkout main
git merge feature/phase-10-privacy-policy
git push origin main
```

---

## What changed

| Item | Location |
|------|----------|
| French policy | `docs/privacy/privacy-policy.fr.md` |
| German policy | `docs/privacy/privacy-policy.de.md` |
| Public API | `GET /api/v1/legal/privacy?lang=fr\|de` |
| Loader | `src/sentinel_suisse/legal/privacy.py` |

No authentication required. Rate-limited like other endpoints.

---

## Data map

All pre-production privacy checklist items are now complete. Remaining work is operational (hosting, legal review, public launch).

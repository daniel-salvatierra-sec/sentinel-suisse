# Phase 36 — Legal foundation & business model

**Branch:** `feature/phase-36-legal-model`  
**Goal:** Terms of Service (5 langs), nLPD checklist, provisional open-vs-paid decision; wire Terms into API + UI consent.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-36-legal-model
```

### Step 2 — Tests

```powershell
$secure = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$env:TEST_ADMIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
pytest -q
```

Expect **85+ passed** (new `test_terms_of_service.py`).

### Step 3 — Manual check (API running)

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/legal/terms?lang=es"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/legal/privacy?lang=es"
```

In the UI footer: **Privacidad** + **Condiciones**. Signup consent mentions both.

### Step 4 — Confirm business model

Read [`docs/legal/business-model.md`](../legal/business-model.md).  
Provisional: **open code + free core alerts**; payments (Twint/Revolut/crypto) **deferred**.

Tell the agent if you want to override.

### Step 5 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: terms of service nLPD checklist and open model (Phase 36)"
git checkout main
git merge feature/phase-36-legal-model
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Docs | `docs/legal/terms.{fr,de,es,pt,en}.md` |
| Checklist | `docs/legal/nlpd-checklist.md` |
| Model | `docs/legal/business-model.md` |
| API | `GET /api/v1/legal/terms?lang=` |
| UI | Footer Terms link + consent text |
| Docker | Copy `docs/privacy` + `docs/legal` into image |
| Versions | `0.36.0` |

## Out of scope

- Lawyer sign-off (you schedule separately)
- Payment integrations (Phase 38+)
- User dashboard redesign (Phase 37 — your Excalidraw)

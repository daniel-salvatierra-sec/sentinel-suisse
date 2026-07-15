# Phase 26 — Interactive guide onboarding (5 languages)

**Branch:** `feature/phase-26-guide`  
**Goal:** Multi-step guide bot (welcome → category → search → map → alerts) with first-visit auto-open; i18n in fr/de/es/pt/en.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-26-guide
```

### Step 2 — UI check

Terminal API (optional) + frontend:

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173** — guide should auto-open on first visit.  
Clear `localStorage` key `suisse-alert-guide-seen` to test again.

### Step 3 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **75 passed** (frontend-only; no new backend tests).

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add multi-step guide onboarding in five languages (Phase 26)"
git checkout main
git merge feature/phase-26-guide
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Guide | `GuideBot.tsx` — 6-step wizard with progress dots |
| Storage | `guideStorage.ts` — first-visit auto-open |
| i18n | New guide strings in all 5 locales |
| CSS | `.guide-modal`, avatar, step dots |
| Versions | API + frontend `0.26.0` |

## Out of scope (Phase 27+)

- Hosting / TLS
- LLM / real conversational AI
- Public search in production flag

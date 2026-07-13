# Phase 12 — Localized alert templates (5 languages)

**Branch:** `feature/phase-12-alert-i18n`  
**Goal:** Email and WhatsApp alert bodies in **fr, de, es, pt, en** based on `users.locale`.

---

## Your steps (run in order)

### Step 1 — Branch + migration

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-12-alert-i18n
pip install -e .
alembic upgrade head
```

### Step 2 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **36 passed**.

### Step 3 — Set user locale (admin API)

Create or patch user with `"locale": "es"` — alerts for that user use Spanish templates.

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: localize alert templates in five languages via user locale"
git checkout main
git merge feature/phase-12-alert-i18n
git push origin main
```

---

## What changed

| Item | Detail |
|------|--------|
| `users.locale` | `fr` default; migration `005` |
| Templates | `src/sentinel_suisse/i18n/alerts.py` |
| Notifiers | email, WhatsApp, console use localized copy |
| API | `locale` on user create/update/read |

---

## Notes

- Existing users get `locale=fr` from migration default.
- Unknown locale falls back to French.

# Phase 9 — Right to erasure (nLPD / GDPR)

**Branch:** `feature/phase-9-erasure`  
**Goal:** Let users and admins permanently delete accounts and all cascaded personal data.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-9-erasure
pip install -r requirements.txt
pip install -e .
```

### Step 2 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = 'your-admin-plain-password'
pytest -q
```

Expect **18 passed** (2 new erasure tests).

### Step 3 — Manual API check (optional)

With uvicorn running:

```powershell
uvicorn sentinel_suisse.main:app --host 127.0.0.1 --port 8000
```

Self-service (user API key):

```powershell
Invoke-RestMethod -Method DELETE -Uri "http://127.0.0.1:8000/api/v1/users/me" -Headers @{ "X-API-Key" = $plainKey }
```

Admin:

```powershell
Invoke-RestMethod -Method DELETE -Uri "http://127.0.0.1:8000/api/v1/users/USER_ID" -Authentication Basic -Credential (New-Object PSCredential("admin", (ConvertTo-SecureString $pass -AsPlainText -Force)))
```

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add right-to-erasure endpoints with cascade delete"
git checkout main
git merge feature/phase-9-erasure
git push origin main
```

---

## What changed

| Endpoint | Auth | Effect |
|----------|------|--------|
| `DELETE /api/v1/users/me` | `X-API-Key` | Self-delete account + cascaded PII |
| `DELETE /api/v1/users/{id}` | Admin Basic | Admin-initiated erasure |

**Cascade (DB FK `ON DELETE CASCADE`):**

- `notification_channels`
- `saved_searches`
- `alerts_log`

Listings are **not** deleted (shared aggregated data).

Response body reports counts removed for audit evidence.

---

## Notes

- Erasure is **irreversible** — no soft-delete in MVP.
- Re-registering with the same email is allowed (new `user_id`, new API key).
- Privacy policy (FR/DE) remains a separate pre-production task.

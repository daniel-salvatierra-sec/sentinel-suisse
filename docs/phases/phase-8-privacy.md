# Phase 8 — PII encryption + raw_payload TTL

**Branch:** `feature/phase-8-privacy`  
**Goal:** Encrypt emails and channel addresses at rest; purge stale `raw_payload` per data map.

---

## Your steps (run in order)

### Step 1 — Branch + deps

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git checkout -b feature/phase-8-privacy
pip install -r requirements.txt
pip install -e .
```

### Step 2 — Generate PII key (required before migration)

```powershell
python scripts/generate_pii_key.py
```

Copy the printed line into `.env` as `PII_ENCRYPTION_KEY=...`

### Step 3 — Migration 004

```powershell
alembic upgrade head
```

If `alembic` fails on DB connection, apply manually with `psql` (see migration `004_pii_encryption.py`).

### Step 4 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = 'your-admin-plain-password'
pytest -q
```

### Step 5 — Purge job (dry run on dev data)

```powershell
python -m sentinel_suisse.maintenance purge-raw-payload --days 30
```

### Step 6 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: encrypt PII at rest and add raw_payload TTL job"
git checkout main
git merge feature/phase-8-privacy
git push origin main
```

---

## What changed

| Area | Change |
|------|--------|
| `security/pii.py` | Fernet encrypt/decrypt + `email_lookup` HMAC |
| `users` | `email_lookup` unique index; `email` stores ciphertext |
| `notification_channels` | `channel_address` encrypted |
| API routes | Encrypt on write, decrypt on read |
| `services/alerts.py` | Decrypt channel before notify |
| `maintenance` | `purge-raw-payload --days N` clears old JSONB |
| Migration `004` | Backfill encrypt existing rows |

---

## Notes

- **Never rotate `PII_ENCRYPTION_KEY`** without a re-encryption migration — existing ciphertext becomes unreadable.
- Legacy plaintext values (no `gAAAA` prefix) are still returned as-is by `decrypt_pii` until migration runs.
- `email_lookup` enables unique constraint without storing plaintext email.

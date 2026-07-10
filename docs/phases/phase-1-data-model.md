# Phase 1 — Data Model (COMPLETED)

**Project:** Sentinel Suisse  
**Author:** Daniel Salvatierra  
**Date completed:** 10 July 2026  
**Branch:** `feature/phase-1-data-model`  
**Database:** PostgreSQL 16.14 (native Windows install, no Docker)

---

## Objective

Define PostgreSQL schema with SQLAlchemy models and Alembic migrations. No API, no ingestion, no alerts — schema and privacy documentation only.

---

## Infrastructure

| Component | Choice |
|-----------|--------|
| PostgreSQL | 16.14, localhost:5432 |
| Database | `sentinel_suisse` |
| User | `sentinel` (local dev only) |
| Python | 3.14.6 |
| ORM | SQLAlchemy 2.0.51 |
| Migrations | Alembic 1.18.5 |

---

## Commands executed (in order)

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git checkout -b feature/phase-1-data-model

# PostgreSQL (SQL Shell as postgres user):
# CREATE USER sentinel WITH PASSWORD 'sentinel';
# CREATE DATABASE sentinel_suisse OWNER sentinel;
# GRANT ALL PRIVILEGES ON DATABASE sentinel_suisse TO sentinel;

pip install -r requirements.txt
pip install -e .
alembic upgrade head

# Verification
alembic current
pre-commit run --all-files
bandit -c pyproject.toml -r src
```

---

## Migration evidence

```
alembic current → 001 (head)
alembic history → Initial schema: providers, listings, users, ...
```

### Tables created (`\dt` in psql)

| Table | Purpose |
|-------|---------|
| `providers` | External portals |
| `listings` | Aggregated ads (dedup via `external_id`, `content_hash`) |
| `users` | Alert subscribers |
| `notification_channels` | WhatsApp / email / Telegram |
| `saved_searches` | JSON filter criteria |
| `alerts_log` | Send audit trail |
| `alembic_version` | Migration tracking |

---

## Security checklist (all passed)

| # | Check | Evidence |
|---|-------|----------|
| 1 | Migration applies cleanly | `alembic upgrade head`, `001 (head)` |
| 2 | No seed data / no default admin | Manual review `001_initial_schema.py` |
| 3 | PII documented | `docs/privacy/data-map.md` |
| 4 | FK: RESTRICT on catalog data | `listings.provider_id`, `alerts_log.listing_id` |
| 5 | FK: CASCADE on user-owned rows | `notification_channels`, `saved_searches` |
| 6 | gitleaks | Passed |
| 7 | ruff | Passed (after line-length fix) |
| 8 | bandit | 0 issues (221 LOC scanned) |
| 9 | `.env` not tracked | Verified in Phase 0 |

### bandit output

```
No issues identified.
Total lines of code: 221
Medium: 0 | High: 0
```

---

## Pre-commit blocked first commit (expected behaviour)

First `git commit` failed on ruff E501 (line too long) and F821 (forward reference). Hooks auto-reformatted files; `provider.py` fixed with `TYPE_CHECKING` import. **This is the security workflow working correctly.**

---

## Next phase

**Phase 2 — Internal CRUD API:** FastAPI endpoints for providers/listings, localhost only, admin auth, rate limiting (`slowapi`).

See [phase-2-internal-crud.md](phase-2-internal-crud.md) when available.

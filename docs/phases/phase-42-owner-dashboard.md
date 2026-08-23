# Phase 42 — Owner dashboard

**Status:** Implemented 2026-08-21  
**Goal:** A private screen where the operator can see and manage LinkSwiss without SSH or raw API calls.

## Why

Production has no cockpit. `/docs` is off. Admin exists only as HTTP Basic CRUD (`/api/v1/users`, `/listings`, `/providers`). Health is `GET /health`. Logs and ingest live on the VPS.

## Scope

- **Auth:** existing HTTP Basic (`ADMIN_USERNAME` / hash). Login form at `/admin` stores the token in `sessionStorage` only. Never linked from the public home UI.
- **Read:** counts of users, Premium, housing vs jobs, direct ads, last ingest freshness by provider.
- **Act:** hide/unhide spam listings (`listings.is_hidden`), erase a user (nLPD), list recent signups, toggle Premium.
- **Out of scope for v1:** Grafana, editing `.env`, running ingest from the browser.

## Notes

- Public product stays search + Cuenta. Dashboard is operator-only (`X-Robots-Tag: noindex`).
- UI language for v1: Spanish.
- `/docs` remains off when `APP_ENV=production`.
- Do not scrape Homegate / ImmoScout / Job-Room; the ingest table shows whatever providers already exist.

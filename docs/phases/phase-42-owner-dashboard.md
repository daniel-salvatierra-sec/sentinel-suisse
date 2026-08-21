# Phase 42 — Owner dashboard (queued)

**Status:** Queued 2026-08-21 — do not start until the operator asks.  
**Goal:** A private screen where the operator can see and manage LinkSwiss without SSH or raw API calls.

## Why

Production has no cockpit. `/docs` is off. Admin exists only as HTTP Basic CRUD (`/api/v1/users`, `/listings`, `/providers`). Health is `GET /health`. Logs and ingest live on the VPS.

## Scope (when building)

- **Auth:** admin only (existing Basic or a dedicated login). Never expose this on the public home UI.
- **Read:** counts of users, Premium, housing vs jobs, direct (user-posted) ads, last ingest freshness by provider.
- **Act:** deactivate spam listings, erase a user (existing nLPD flow), list recent signups.
- **Out of scope for v1:** Grafana, editing `.env`, running ingest from the browser.

## Notes

- Public product stays search + Cuenta. Dashboard is operator-only.
- Five UI languages not required for v1 (French or Spanish is enough).
- Do not scrape Homegate / ImmoScout / Job-Room; dashboard must not imply those feeds.

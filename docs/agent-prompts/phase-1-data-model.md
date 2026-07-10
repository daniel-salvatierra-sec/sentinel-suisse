# Phase 1 — Data model (agent prompt)

Build SQLAlchemy models and Alembic migration only. **No business logic, no API endpoints.**

## Explicit security instructions

- Use strict column types and `NOT NULL` where appropriate.
- **No seed data** in migrations — no default admin user, no predictable passwords.
- Foreign keys: `RESTRICT` on `listings.provider_id` and `alerts_log.listing_id` (prevent accidental cascade deletes of catalog data).
- `CASCADE` only on user-owned rows (`notification_channels`, `saved_searches`).
- Document PII fields in `docs/privacy/data-map.md`; encryption at rest is planned, not implemented yet.
- `saved_searches.query` must be JSONB with API-layer Pydantic validation later — not raw SQL strings.

## Models

- `providers`, `listings`, `users`, `notification_channels`, `saved_searches`, `alerts_log`
- `listings`: `external_id`, `content_hash`, `source_url`, `listing_type`, `raw_payload` (JSONB, TTL planned)

## Do not

- Hardcode credentials or connection strings (use `DATABASE_URL` env var).
- Include example rows with real emails or phone numbers.

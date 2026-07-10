# Phase 2 — Internal CRUD API (agent prompt)

Build FastAPI CRUD for `providers` and `listings`. **Localhost only. Not deployed publicly.**

## Explicit security instructions

- All DB access via SQLAlchemy ORM (`select`, `db.get`) — **never** f-strings or raw SQL concatenation.
- Validate all inputs with Pydantic before touching the database.
- Protect every mutating and listing endpoint with admin auth (`HTTPBasic` + bcrypt hash from env).
- Admin password: store **only** `ADMIN_PASSWORD_HASH` in `.env`, never plaintext.
- Use `secrets.compare_digest` for username comparison.
- Rate limit all routes with `slowapi` (default `30/minute`).
- Bind server to `127.0.0.1` only — never `0.0.0.0` in Phase 2.
- Run `bandit -r src` after each block; no medium/high findings.

## Endpoints

- `GET/POST/PATCH/DELETE /api/v1/providers`
- `GET/POST/PATCH/DELETE /api/v1/listings`
- `GET /health` (no auth — minimal, rate-limited)

## Do not

- Expose Swagger publicly in production (`docs_url=None` when `APP_ENV!=development`).
- Log credentials or connection strings.

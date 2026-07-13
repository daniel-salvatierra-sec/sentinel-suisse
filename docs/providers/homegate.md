# Homegate — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default)

## Before enabling live ingest

- [ ] Read [Homegate terms of use](https://www.homegate.ch/c/en/about-us/legal-issues/terms-and-conditions)
- [ ] Check `https://www.homegate.ch/robots.txt`
- [ ] No public API — parser reads embedded `window.__INITIAL_STATE__` on search pages
- [ ] Set `INGEST_HOMEGATE_LIVE=true` only after legal review

## Technical (Phase 13)

- Search URL pattern: `https://www.homegate.ch/mieten/immobilien/<region>/trefferliste`
- Parser path: `resultList.search.fullSearch.result.listings`
- Identifiable `User-Agent` via `INGEST_USER_AGENT` / `ingest_user_agent` in settings
- Rate limit: `INGEST_RATE_LIMIT_SECONDS` (default 3s before each request)
- Idempotent upsert via `(provider_id, external_id)` + `content_hash`
- Pilot fixture still supported: `--fixture fixtures/homegate_sample.json`

## CLI

```powershell
# Fixture (always safe)
python -m sentinel_suisse.ingest --provider homegate --fixture fixtures/homegate_sample.json

# Live (requires INGEST_HOMEGATE_LIVE=true in .env)
python -m sentinel_suisse.ingest --provider homegate --live
```

## Limitations (MVP)

- Single search page per run (no pagination yet)
- Housing rent focus; listing type mapped to `housing`
- Property detail pages use Pinia state — not implemented in this phase

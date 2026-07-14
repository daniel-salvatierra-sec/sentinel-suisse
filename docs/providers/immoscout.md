# ImmoScout24.ch — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default)

## Before enabling live ingest

- [ ] Read [ImmoScout24 terms of use](https://www.immoscout24.ch/fr/about/conditions-generales)
- [ ] Check `https://www.immoscout24.ch/robots.txt`
- [ ] No public API — parser reads embedded JSON on search pages
- [ ] Set `INGEST_IMMOSCOUT_LIVE=true` only after legal review

## Technical (Phase 21)

- Search URL default: Geneva rentals (`immoscout_search_url` in settings)
- Parser tries common embedded state markers (`__INITIAL_STATE__`, `__NEXT_DATA__`, etc.)
- Identifiable `User-Agent` via `INGEST_USER_AGENT`
- Rate limit: `INGEST_RATE_LIMIT_SECONDS` (default 3s)
- Idempotent upsert via `(provider_id, external_id)` + `content_hash`
- Pilot fixture: `--fixture fixtures/immoscout_sample.json`

## CLI

```powershell
# Fixture (always safe)
python -m sentinel_suisse.ingest --provider immoscout --fixture fixtures/immoscout_sample.json

# Live (requires INGEST_IMMOSCOUT_LIVE=true in .env)
python -m sentinel_suisse.ingest --provider immoscout --live
```

## Limitations (MVP)

- Single search page per run (no pagination yet)
- Housing focus; `listing_type=housing`
- Live HTML shape may change — fixture ingest remains the reliable dev path

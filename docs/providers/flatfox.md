# Flatfox — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default)

## Before enabling live ingest

- [ ] Read [Flatfox terms of use](https://flatfox.ch/en/terms/)
- [ ] Check `https://flatfox.ch/robots.txt`
- [ ] No public API — parser reads embedded JSON on search pages
- [ ] Set `INGEST_FLATFOX_LIVE=true` only after legal review

## Technical (Phase 20)

- Search URL default: Geneva region (`flatfox_search_url` in settings)
- Parser tries common embedded state markers (`__INITIAL_STATE__`, `__NEXT_DATA__`, etc.)
- Identifiable `User-Agent` via `INGEST_USER_AGENT`
- Rate limit: `INGEST_RATE_LIMIT_SECONDS` (default 3s)
- Idempotent upsert via `(provider_id, external_id)` + `content_hash`
- Pilot fixture: `--fixture fixtures/flatfox_sample.json`

## CLI

```powershell
# Fixture (always safe)
python -m sentinel_suisse.ingest --provider flatfox --fixture fixtures/flatfox_sample.json

# Live (requires INGEST_FLATFOX_LIVE=true in .env)
python -m sentinel_suisse.ingest --provider flatfox --live
```

## Limitations (MVP)

- Single search page per run (no pagination yet)
- Housing focus; `listing_type=housing`
- Live HTML shape may change — fixture ingest remains the reliable dev path

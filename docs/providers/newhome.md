# newhome.ch — legal / technical notes

**Status:** Live connector scaffolded (opt-in, disabled by default). Fixture ingest ready.

## Before enabling live ingest

- [ ] Read newhome.ch terms of use
- [ ] Check `https://www.newhome.ch/robots.txt`
- [ ] Confirm HTML/embedded-state parse still matches connector paths
- [ ] Set `INGEST_NEWHOME_LIVE=true` only after legal review

## Technical (Phase 40)

- Default search URL: `NEWHOME_SEARCH_URL` (Geneva rent focus)
- Parser reads embedded `window.__INITIAL_STATE__` / `__NEXT_DATA__` / `__NUXT__`
- Identifiable `User-Agent` via `INGEST_USER_AGENT`
- Rate limit: `INGEST_RATE_LIMIT_SECONDS`
- Pilot fixture: `fixtures/newhome_sample.json`

## CLI

```powershell
python -m sentinel_suisse.ingest --provider newhome --fixture fixtures/newhome_sample.json
python -m sentinel_suisse.ingest --provider newhome --live
```

## Limitations (MVP)

- Single search page per run (no pagination)
- Live shape may change — fixture ingest remains the reliable path
- Provider name is never shown in the public UI

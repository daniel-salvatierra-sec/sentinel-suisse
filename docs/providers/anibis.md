# anibis.ch — legal / technical notes

**Status:** Live connector scaffolded (opt-in, disabled by default). Fixture ingest ready.

## Before enabling live ingest

- [ ] Read anibis.ch terms of use
- [ ] Check `https://www.anibis.ch/robots.txt`
- [ ] Confirm HTML/embedded-state parse still matches connector paths
- [ ] Set `INGEST_ANIBIS_LIVE=true` only after legal review

## Technical (Phase 40)

- Default search URL: `ANIBIS_SEARCH_URL` (Geneva immobilier)
- Parser reads embedded `window.__INITIAL_STATE__` / `__NEXT_DATA__` / `__NUXT__`
- Identifiable `User-Agent` via `INGEST_USER_AGENT`
- Rate limit: `INGEST_RATE_LIMIT_SECONDS`
- Pilot fixture: `fixtures/anibis_sample.json`

## CLI

```powershell
python -m sentinel_suisse.ingest --provider anibis --fixture fixtures/anibis_sample.json
python -m sentinel_suisse.ingest --provider anibis --live
```

## Limitations (MVP)

- Housing focus only in this phase
- Live HTML shape may change — fixture ingest remains the reliable path
- Provider name is never shown in the public UI

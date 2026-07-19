# Indeed France — legal / technical notes

**Status:** Live connector scaffolded (opt-in, disabled by default). Fixture ingest ready. Listings tagged `country=FR`.

## Before enabling live ingest

- [ ] Read Indeed terms of use
- [ ] Check `https://fr.indeed.com/robots.txt`
- [ ] Confirm HTML/embedded-state parse still matches connector paths
- [ ] Set `INGEST_INDEED_FR_LIVE=true` only after legal review

## Technical (Phase 41)

- Default search URL: `INDEED_FR_SEARCH_URL` (Annemasse / 25 km)
- Parser reads embedded `window.__NEXT_DATA__` (and fallbacks)
- Pilot fixture: `fixtures/indeed_fr_sample.json`

## CLI

```powershell
python -m sentinel_suisse.ingest --provider indeed_fr --fixture fixtures/indeed_fr_sample.json
python -m sentinel_suisse.ingest --provider indeed_fr --live
```

## Limitations (MVP)

- Single search page per run
- Live shape may change — fixture ingest remains the reliable path
- Provider name is never shown in the public UI

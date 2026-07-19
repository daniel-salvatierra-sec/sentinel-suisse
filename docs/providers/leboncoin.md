# Leboncoin (FR) — legal / technical notes

**Status:** Live connector scaffolded (opt-in, disabled by default). Fixture ingest ready. Listings tagged `country=FR`.

## Before enabling live ingest

- [ ] Read Leboncoin terms of use / conditions d'utilisation
- [ ] Check `https://www.leboncoin.fr/robots.txt`
- [ ] Confirm HTML/embedded-state parse still matches connector paths
- [ ] Set `INGEST_LEBONCOIN_LIVE=true` only after legal review

## Technical (Phase 41)

- Default search URL: `LEBONCOIN_SEARCH_URL` (Annemasse / border focus)
- Parser reads embedded `window.__NEXT_DATA__` (and fallbacks)
- Pilot fixture: `fixtures/leboncoin_sample.json`

## CLI

```powershell
python -m sentinel_suisse.ingest --provider leboncoin --fixture fixtures/leboncoin_sample.json
python -m sentinel_suisse.ingest --provider leboncoin --live
```

## Limitations (MVP)

- Rentals focus for Geneva border
- Live HTML shape may change — fixture ingest remains the reliable path
- Provider name is never shown in the public UI

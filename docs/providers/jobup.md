# jobup.ch — legal / technical notes

**Status:** Live connector scaffolded (opt-in, disabled by default). Fixture ingest ready.

## Before enabling live ingest

- [ ] Read jobup.ch terms of use
- [ ] Check `https://www.jobup.ch/robots.txt`
- [ ] Confirm HTML/embedded-state parse still matches connector paths
- [ ] Set `INGEST_JOBUP_LIVE=true` only after legal review

## Technical (Phase 40)

- Default search URL: `JOBUP_SEARCH_URL` (Geneva jobs)
- Parser reads embedded `window.__NEXT_DATA__` when present, otherwise schema.org JSON-LD `JobPosting` items on the search page
- Maps employment type and workload when present
- Identifiable `User-Agent` via `INGEST_USER_AGENT`
- Rate limit: `INGEST_RATE_LIMIT_SECONDS`
- Pilot fixture: `fixtures/jobup_sample.json`

## CLI

```powershell
python -m sentinel_suisse.ingest --provider jobup --fixture fixtures/jobup_sample.json
python -m sentinel_suisse.ingest --provider jobup --live
```

## Limitations (MVP)

- Up to `JOBCLOUD_MAX_PAGES` (default 3) per city per hourly run, plus extra role-keyword passes for logistics hubs
- Live HTML shape may change — fixture ingest remains the reliable path
- Provider name is never shown in the public UI

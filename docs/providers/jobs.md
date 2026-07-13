# jobs.ch — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default)

## Before enabling live ingest

- [ ] Read [jobs.ch terms](https://www.jobs.ch/en/legal/terms-and-conditions/)
- [ ] Check `https://www.jobs.ch/robots.txt`
- [ ] No public API — parser reads embedded page state (`__NEXT_DATA__` / `__INITIAL_STATE__`)
- [ ] Set `INGEST_JOBS_LIVE=true` only after legal review

## Technical (Phase 14)

- Default search: Geneva vacancies (English UI path)
- `listing_type`: `job` (no salary in MVP unless source provides it)
- Same rate limit and User-Agent as Homegate ingest
- Fixture: `fixtures/jobs_sample.json`

## CLI

```powershell
# Register provider once (admin API)
# {"name":"jobs.ch","slug":"jobs","base_url":"https://www.jobs.ch","is_active":true}

python -m sentinel_suisse.ingest --provider jobs --fixture fixtures/jobs_sample.json
python -m sentinel_suisse.ingest --provider jobs --live
```

## Limitations (MVP)

- Single search page per run
- Live HTML shape may change — parser tries multiple embedded markers

# Adzuna — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official,
self-serve, no scraping** — same category as France Travail, but self-signup instead
of waiting for an email reply, and covers both Switzerland and France.

## Why this connector is different

Adzuna is a job-board *aggregator* whose entire business model is redistributing job
ads to third-party sites via API. Their own docs describe this exact use case:

> "Get job ads to display on your own website. Use Adzuna's up-to-the-minute
> employment data to power your own website, reporting and data visualisations."
> (developer.adzuna.com)

No robots.txt concerns, no ToS conflict, no waiting on a partner's approval — this is
the intended, self-serve use case. It already indirectly aggregates thousands of
public sources per country (it does the scraping/partnership work upstream so we
don't have to), which is also a pragmatic way to get real Swiss/French listings while
outreach to SECO/SMG (docs/outreach/) is pending.

## Before enabling live ingest

- [ ] Register a free account at <https://developer.adzuna.com/signup>
- [ ] Copy the `app_id` / `app_key` shown on the dashboard
- [ ] Set `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` in `.env`
- [ ] Set `INGEST_ADZUNA_LIVE=true`

## Technical

- Auth: `app_id` + `app_key` as query params on every request (no OAuth).
- Search: `GET https://api.adzuna.com/v1/api/jobs/{country}/search/1`, where
  `{country}` is `ADZUNA_COUNTRY` (`ch` for Switzerland, `fr` for France — one
  Adzuna account can query multiple countries, but ingest runs one country per call;
  run twice with different `ADZUNA_COUNTRY`/provider rows to cover both).
- `ADZUNA_KEYWORDS` -> `what`, `ADZUNA_LOCATION` -> `where`.
- `listing_type`: always `job`. `country`: mapped from `ADZUNA_COUNTRY` (`ch`/`fr`).
- Free tier limits: 25 requests/min, 250/day, 2 500/month — comfortably enough for a
  periodic batch ingest job (e.g. hourly cron), not meant for live per-user-search
  calls.
- Fixture: `fixtures/adzuna_sample.json` (raw API response shape, used by the
  connector's own unit tests — not the generic `--fixture` CLI loader).

## CLI

```powershell
# Live (requires ADZUNA_APP_ID/APP_KEY + INGEST_ADZUNA_LIVE=true)
python -m sentinel_suisse.ingest --provider adzuna --live
```

Register the provider once via the admin API before the first run:

```powershell
# {"name":"Adzuna","slug":"adzuna","base_url":"https://www.adzuna.com","is_active":true}
```

## Limitations (MVP)

- Single page per run (`results_per_page=50`) — no pagination loop yet
- One country per run — `ADZUNA_COUNTRY` picks `ch` or `fr`; running both means two
  provider rows / two scheduled runs
- Category comes from Adzuna's own taxonomy (`category.label`), not ours — matching
  against saved-search `job_category` filters may need a mapping layer later
- `salary_min` is used as `price` when present, but note Adzuna sometimes shows an
  *estimated* salary (`salary_is_predicted`) rather than one stated in the ad — not
  distinguished yet

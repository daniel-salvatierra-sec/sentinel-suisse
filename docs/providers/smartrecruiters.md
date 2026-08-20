# SmartRecruiters — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official, keyless,
no scraping.** No signup, no API key, no rate-limit tier — the friendliest connector in
the project.

## Why this connector exists

SmartRecruiters (an Applicant Tracking System, ATS) publishes a public, unauthenticated
"Postings API" for every company that hosts its career site on it:

```
GET https://api.smartrecruiters.com/v1/companies/{companyIdentifier}/postings
```

This is the exact same data that powers a company's own
`jobs.smartrecruiters.com/<companyIdentifier>` careers page, and SmartRecruiters
explicitly documents it for third-party job-board syndication. Reading it is not
scraping — no HTML parsing, no ToS conflict, no `robots.txt` concerns.

### Confirmed Geneva-area employers on SmartRecruiters

Researched by checking each employer's public careers page for a
`careers.smartrecruiters.com/<company>` or `jobs.smartrecruiters.com/<company>` link:

- **HUG** (Hôpitaux Universitaires de Genève) — company identifier `HUG`. One of the
  largest employers in the canton (~13,000 employees, 150+ professions).
- **SGS** (Geneva-headquartered testing/inspection/certification group, ~99,000
  employees globally) — company identifier `SGS`. Uses Workday internally but
  syndicates external job ads via SmartRecruiters.

Other large Geneva employers researched but **not** on SmartRecruiters (for future
connectors, see Limitations below):

- Genève Aéroport (GVA) — proprietary in-house careers portal at `gva.ch/emplois`.
- CERN — proprietary careers portal at `careers.cern`.
- Richemont — Workday (`careers.richemont.com`), requires a different connector
  (Workday's CXS JSON endpoint, `POST {domain}/wday/cxs/{tenant}/{site}/jobs`).
- Pictet — SAP SuccessFactors (no public jobs JSON API).
- Lombard Odier — Workday CXS; see `docs/providers/lombard-odier.md`.
- BCGE — Adequasys (`jobs.bcge.ch`), proprietary HTML, skip.

## Before enabling live ingest

- [ ] Confirm the company identifiers you want in `SMARTRECRUITERS_COMPANIES`
  (comma-separated, e.g. `HUG,SGS`) — find them in the company's
  `jobs.smartrecruiters.com/<identifier>` URL.
- [ ] Set `INGEST_SMARTRECRUITERS_LIVE=true`

No account, no key, nothing else to configure.

## Technical

- Auth: none.
- List: `GET .../companies/{company}/postings?limit=100&offset=0`, paginated using
  `totalFound` from the response until `offset >= totalFound`.
- Detail (optional, `SMARTRECRUITERS_FETCH_DETAILS=true` by default): one extra
  `GET .../companies/{company}/postings/{id}` call per posting to pull the full job
  description (`jobAd.sections.*.text`) and the canonical `postingUrl`/`applyUrl`. This
  multiplies the number of requests by roughly the posting count — with the default
  `INGEST_RATE_LIMIT_SECONDS=3` a company with ~65 open postings takes a few minutes per
  run, which is fine for an hourly/daily cron but not for a live per-user-search call.
  Set `SMARTRECRUITERS_FETCH_DETAILS=false` to skip the detail call and keep only the
  list-level fields (title, city, industry, contract type) if faster/lighter runs are
  preferred.
- `listing_type`: always `job`. `country`: read from `location.country` on each
  posting (`ch`/`fr`); postings outside CH/FR are silently skipped since the app only
  supports those two countries.
- Location translation: SmartRecruiters returns Swiss Romande/German city names in
  their local language (`Genève`, `Zürich`) — translated to the app's English
  convention (`Geneva`, `Zurich`) to match the rest of the search index.
- Fixtures: `fixtures/smartrecruiters_sample.json` (list response) and
  `fixtures/smartrecruiters_detail_sample.json` (detail response) — used by the
  connector's own unit tests, not the generic `--fixture` CLI loader.

## CLI

```powershell
# Live (no credentials needed, just INGEST_SMARTRECRUITERS_LIVE=true)
python -m sentinel_suisse.ingest --provider smartrecruiters --live
```

Register the provider once via the admin API before the first run:

```json
{"name":"SmartRecruiters","slug":"smartrecruiters","base_url":"https://www.smartrecruiters.com","is_active":true}
```

## Limitations (MVP)

- One connector run covers all companies in `SMARTRECRUITERS_COMPANIES` — no per-company
  provider rows; all postings are attributed to the single `smartrecruiters` provider
  slug in the ingest stats.
- `job_category` comes from SmartRecruiters' own `industry.label` taxonomy, not ours —
  matching against saved-search `job_category` filters may need a mapping layer later.
- No salary data — SmartRecruiters postings rarely include it, so `price` is always
  `None`.
- Detail-call enrichment is best-effort: if a detail request fails (rate limit,
  transient error), the listing still gets created using only the list-level fields
  (title, city, contract type) rather than failing the whole run.

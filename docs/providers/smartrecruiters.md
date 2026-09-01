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

The API accepts `?country=ch|fr|de|it`. We always pass that filter and paginate per
country so a global employer (SGS has thousands of worldwide ads) never dumps the
whole planet into LinkSwiss.

### Confirmed employers on SmartRecruiters (default `SMARTRECRUITERS_COMPANIES`)

Identifiers are the token in `jobs.smartrecruiters.com/<identifier>`:

- **HUG** — Hôpitaux Universitaires de Genève.
- **CERN** — public SR postings exist (do **not** scrape `careers.cern`).
- **Imad** — Geneva home-care (institution genevoise de maintien à domicile).
- **HospiceGeneral** — Hospice général, Genève / Lancy.
- **SGS** — Geneva HQ, global ads. Connector keeps only CH/FR/DE/IT.

Guessed IDs that returned 403/404 (skipped at runtime, do not scrape HTML instead):
GVA, Rolex, TPG, CHUV, ICRC, MSF, LVMH (Paris-only — not useful).

Other large Geneva employers **not** on this API:

- Genève Aéroport — proprietary portal at `gva.ch/emplois`.
- Richemont / Lombard Odier / Logitech / P&G / Temenos — Workday CXS (separate
  connectors).
- Pictet — SAP SuccessFactors (no public jobs JSON).
- BCGE — Adequasys HTML, skip.

## Before enabling live ingest

On the VPS `.env` (git pull alone does **not** turn ingest on):

```
INGEST_SMARTRECRUITERS_LIVE=true
SMARTRECRUITERS_COMPANIES=HUG,CERN,Imad,HospiceGeneral,SGS
```

Then cron, e.g. every 6 hours:

```
30 */6 * * * /opt/sentinel-suisse/deploy/run-ingest.sh smartrecruiters >> /var/log/linkswiss-ingest.log 2>&1
```

Provider row `smartrecruiters` is seeded by Alembic `019`. No admin API POST needed
after `alembic upgrade head`.

## Technical

- Auth: none.
- List: `GET .../companies/{company}/postings?limit=100&offset=0&country={ch|fr|de|it}`,
  paginated using `totalFound` until `offset >= totalFound`. One unknown company
  (HTTP 403/404) is skipped with a warning; the rest of the run continues.
- Detail (optional, `SMARTRECRUITERS_FETCH_DETAILS=true` by default): one extra
  `GET .../companies/{company}/postings/{id}` call per posting to pull the full job
  description (`jobAd.sections.*.text`) and the canonical `postingUrl`/`applyUrl`.
  With `INGEST_RATE_LIMIT_SECONDS=3`, several companies × four countries takes
  minutes — fine for cron, not for a live per-user search. Set
  `SMARTRECRUITERS_FETCH_DETAILS=false` to keep only list-level fields.
- `listing_type`: always `job`. `country`: `location.country` (`ch`/`fr`/`de`/`it`).
  Other countries are dropped.
- Location translation: `Genève`/`Genf` → `Geneva`, `Zürich` → `Zurich`, etc.
- Fixtures: `fixtures/smartrecruiters_sample.json` and
  `fixtures/smartrecruiters_detail_sample.json`.

## CLI

```powershell
# Live (no credentials needed, just INGEST_SMARTRECRUITERS_LIVE=true)
python -m sentinel_suisse.ingest --provider smartrecruiters --live
```

## Limitations (MVP)

- One connector run covers all companies in `SMARTRECRUITERS_COMPANIES` — no
  per-company provider rows; all postings use the `smartrecruiters` slug.
- `job_category` comes from SmartRecruiters' `industry.label`.
- No salary data — `price` is always `None`.
- Detail-call enrichment is best-effort: if a detail request fails, the listing is
  still created from list-level fields.

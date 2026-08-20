# Richemont — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official,
keyless, no scraping.** No signup, no API key.

## Why this connector is different

`careers.richemont.com` is a Workday-hosted career site. Every Workday career site is a
client-side app that calls a public, keyless JSON API underneath ("Candidate Experience
Service", CXS) — reading it directly is exactly what the site's own JavaScript does,
just without executing a browser. Confirmed by decomposing a real job link from the
public site:

```
POST https://richemont.wd3.myworkdayjobs.com/wday/cxs/richemont/broadbean_external/jobs
Content-Type: application/json

{"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}
```

Richemont's group HQ is in Bellevue (Geneva) and it runs several manufacture/watchmaking
sites in the Jura arc (Le Locle, Les Breuleux, Le Sentier, Villeret, Neuchâtel) — one of
the larger multi-site employers in French-speaking Switzerland once all Maisons
(Cartier, Van Cleef & Arpels, IWC, Vacheron Constantin, Jaeger-LeCoultre, Piaget,
Buccellati, etc.) are counted together.

## Why this connector needs an extra filtering step

Richemont posts jobs globally (419+ open roles across every country when checked), so
unlike the other connectors this one must filter a large multi-country result set down
to Switzerland/France:

1. The list-level search results only carry a city name (`locationsText`), not a
   country code — Workday only puts a reliable, machine-readable country code
   (`jobRequisitionLocation.country.alpha2Code`) on the **per-posting detail** endpoint.
2. So the connector first fetches the "locations" facet (one lightweight request) and
   matches its descriptors against a curated list of known CH/FR place names
   (`_LOCATION_HINTS` in `richemont.py`) to build a candidate list of location IDs.
3. It then pages through only those locations via `appliedFacets.locations`.
4. For every candidate posting it fetches the detail endpoint anyway (needed for the
   full job description), and uses that response's authoritative country code as the
   final CH/FR filter — so a stray false-positive match in step 2 is harmless (one
   wasted request), while a missing name in the curated list is the real risk (a CH/FR
   posting could be skipped until the list is updated).

If Richemont opens a site in a city not already in `_LOCATION_HINTS`, add it via
`RICHEMONT_EXTRA_LOCATION_HINTS` (comma-separated, case-insensitive) without a code
change.

## Before enabling live ingest

- [ ] Set `INGEST_RICHEMONT_LIVE=true`

No account, no key, nothing else required.

## Technical

- Auth: none.
- Search: `POST .../wday/cxs/richemont/broadbean_external/jobs`. Page size is capped by
  the tenant's Workday config — confirmed `limit=20` works, `limit=50`/`100` return
  `HTTP 400`.
- Detail: `GET .../wday/cxs/richemont/broadbean_external{externalPath}` with
  `Accept: application/json` — returns the full HTML job description
  (`jobPostingInfo.jobDescription`, stripped to plain text by the connector), the
  authoritative country (`jobRequisitionLocation.country.alpha2Code`), and the canonical
  apply URL (`jobPostingInfo.externalUrl`).
- One detail call per candidate posting (CH/FR-matched cities only, not all 400+ global
  postings) — with the default `INGEST_RATE_LIMIT_SECONDS=3`, a run covering ~150
  candidate postings (Richemont's typical Geneva + Jura arc + Paris volume) takes
  roughly 7–10 minutes. Fine for a periodic cron, not for a live per-user-search call.
- `job_category` is repurposed to hold the hiring Maison/brand name (e.g. "Cartier",
  "Van Cleef & Arpels") since Richemont doesn't expose a job-function facet per
  posting — this is more useful context for a luxury-goods listing than a generic
  category would be.
- `employment_type` is inferred from the job title (Stage/Intern → internship,
  CDD/Fixed Term/Temporary/Seasonal → temporary, Freelance → freelance, else
  permanent) since the detail endpoint doesn't expose the contract-type facet directly.
- Fixtures: `fixtures/richemont_facets_sample.json`, `richemont_search_sample.json`,
  `richemont_detail_geneva_sample.json`, `richemont_detail_paris_sample.json` — used by
  the connector's own unit tests, not the generic `--fixture` CLI loader.

## CLI

```powershell
# Live (no credentials needed, just INGEST_RICHEMONT_LIVE=true)
python -m sentinel_suisse.ingest --provider richemont --live
```

Register the provider once via the admin API before the first run:

```json
{"name":"Richemont","slug":"richemont","base_url":"https://careers.richemont.com","is_active":true}
```

## Limitations (MVP)

- Relies on a curated, maintained list of CH/FR place names to decide which locations
  to page through — not a full country-facet filter (Workday doesn't expose one on
  this tenant). Extend via `RICHEMONT_EXTRA_LOCATION_HINTS` if a new site is missed.
- No salary data — Richemont/Workday postings don't expose it, so `price` is always
  `None`.
- `job_category` holds the Maison/brand name, not a job-function taxonomy — matching
  against saved-search `job_category` filters may need a mapping layer later.

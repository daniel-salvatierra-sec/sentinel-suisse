# Lombard Odier — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official,
keyless, no scraping.** Same Workday CXS API as Richemont.

## Why this connector exists

Lombard Odier is a Geneva-headquartered private bank (~2,900 employees, 25+ offices).
Its public careers site is Workday-hosted:

```
https://lombardodier.wd3.myworkdayjobs.com/Lombard_Odier_Careers
```

The shared client in `src/sentinel_suisse/ingest/connectors/workday.py` reads the same
JSON API the site's own JavaScript calls. Pictet (SuccessFactors) and BCGE (Adequasys)
do **not** expose an equivalent public JSON API, so they are not in this connector.

## Before enabling live ingest

- [ ] Set `INGEST_LOMBARD_ODIER_LIVE=true`

No account, no key. `LOMBARD_ODIER_EXTRA_LOCATION_HINTS` is optional (comma-separated
CH/FR place names if a new Swiss/French office is missing from the shared hint list).

## Technical

- Auth: none.
- Search: `POST .../wday/cxs/lombardodier/Lombard_Odier_Careers/jobs` (`limit=20`).
- Detail: `GET .../wday/cxs/lombardodier/Lombard_Odier_Careers{externalPath}` with
  `Accept: application/json`.
- CH/FR/DE/IT filter: location-facet heuristic (border cities included), then
  authoritative `jobRequisitionLocation.country.alpha2Code` on each detail
  (London/Singapore/etc. are dropped).
- `external_id`: `lombard-odier-{jobReqId}`.
- Volume is much smaller than Richemont (typically a few dozen global roles, a handful
  in Geneva/Paris). Rate-limit default (`INGEST_RATE_LIMIT_SECONDS=3`) is fine.
- Reuses Richemont JSON fixtures in unit tests (same CXS response shape).

## CLI

```powershell
python -m sentinel_suisse.ingest --provider lombard-odier --live
```

Register the provider once via the admin API before the first run **only if Alembic
`019` has not been applied**:

```json
{"name":"Lombard Odier","slug":"lombard-odier","base_url":"https://www.lombardodier.com/home/careers.html","is_active":true}
```

## Other Geneva banks (not this connector)

- **Pictet** — SAP SuccessFactors (`career5.successfactors.eu?company=banquepict`).
  Legacy career portal, no documented public jobs JSON API. Skip for now.
- **BCGE** — Adequasys (`jobs.bcge.ch`). ~5 openings, proprietary HTML. Skip.
- **Logitech** — Workday CXS (`logitech.wd5` / site `Logitech`); see `docs/providers/logitech.md`.

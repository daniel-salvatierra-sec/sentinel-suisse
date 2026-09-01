# Procter & Gamble — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official,
keyless, no scraping.** Same Workday CXS API as Richemont, Lombard Odier, and Logitech.

## Why this connector exists

P&G's Geneva office (Petit-Lancy) is the group's **European headquarters** (~2,000
employees, Fabric & Home Care / Baby / Beauty plus an AI hub). Careers live at:

```
https://pg.wd5.myworkdayjobs.com/1000
```

The shared client in `src/sentinel_suisse/ingest/connectors/workday.py` reads the same
JSON API the site's own JavaScript calls. CH/FR/DE/IT (Geneva, Schlieren/Zurich,
Amiens/Paris, border cities); US/Asia postings are dropped after the detail
`alpha2Code` check. Inland DE/IT volume stays on Adzuna.

## Before enabling live ingest

- [ ] Set `INGEST_PROCTER_GAMBLE_LIVE=true`

No account, no key. `PROCTER_GAMBLE_EXTRA_LOCATION_HINTS` is optional
(comma-separated CH/FR place names if a Swiss/French site is missing from the
shared hint list). Petit-Lancy, Lancy, and Schlieren are already in that list.

## Technical

- Auth: none.
- Search: `POST .../wday/cxs/pg/1000/jobs` (`limit=20`).
- Detail: `GET .../wday/cxs/pg/1000{externalPath}` with `Accept: application/json`.
- `external_id`: `procter-gamble-{jobReqId}`.
- Reuses Richemont JSON fixtures in unit tests (same CXS response shape).

## CLI

```powershell
python -m sentinel_suisse.ingest --provider procter-gamble --live
```

Register the provider once via the admin API before the first run **only if Alembic
`019` has not been applied**:

```json
{"name":"Procter & Gamble","slug":"procter-gamble","base_url":"https://pg.wd5.myworkdayjobs.com/1000","is_active":true}
```

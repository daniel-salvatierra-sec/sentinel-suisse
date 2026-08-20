# Logitech — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official,
keyless, no scraping.** Same Workday CXS API as Richemont and Lombard Odier.

## Why this connector exists

Logitech is headquartered at the Daniel Borel Innovation Center in Lausanne
(Romandie; commuting distance from Geneva). Its public careers site is Workday-hosted:

```
https://logitech.wd5.myworkdayjobs.com/Logitech
```

The shared client in `src/sentinel_suisse/ingest/connectors/workday.py` reads the same
JSON API the site's own JavaScript calls.

## Employers checked instead of this (not this connector)

| Employer | ATS | Why skipped |
|---|---|---|
| dsm-firmenich | Eightfold PCSX | List JSON returns HTTP 403 `Not authorized for PCSX` |
| Givaudan (Vernier HQ) | Phenom People | SPA, no public jobs JSON |

## Before enabling live ingest

- [ ] Set `INGEST_LOGITECH_LIVE=true`

No account, no key. `LOGITECH_EXTRA_LOCATION_HINTS` is optional (comma-separated
CH/FR place names if a Swiss/French office is missing from the shared hint list).

## Technical

- Auth: none.
- Search: `POST .../wday/cxs/logitech/Logitech/jobs` (`limit=20`).
- Detail: `GET .../wday/cxs/logitech/Logitech{externalPath}` with
  `Accept: application/json`.
- CH/FR filter: location-facet heuristic, then authoritative
  `jobRequisitionLocation.country.alpha2Code` on each detail.
- `external_id`: `logitech-{jobReqId}`.
- Reuses Richemont JSON fixtures in unit tests (same CXS response shape).

## CLI

```powershell
python -m sentinel_suisse.ingest --provider logitech --live
```

Register the provider once via the admin API before the first run:

```json
{"name":"Logitech","slug":"logitech","base_url":"https://logitech.wd5.myworkdayjobs.com/Logitech","is_active":true}
```

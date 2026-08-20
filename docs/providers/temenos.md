# Temenos — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official,
keyless, no scraping.** Same Workday CXS API as Richemont, Lombard Odier, Logitech,
and P&G.

## Why this connector exists

Temenos is a Geneva-headquartered banking-software company (HQ at Pont-Rouge,
Lancy; ~4,500 staff). Its public careers site is Workday-hosted:

```
https://temenos.wd103.myworkdayjobs.com/Temenoscareers
```

The shared client in `src/sentinel_suisse/ingest/connectors/workday.py` reads the same
JSON API the site's own JavaScript calls. CH/FR only; India/UK/US postings are
dropped after the detail `alpha2Code` check.

## Employers checked instead of this (not this connector)

| Employer | ATS | Why skipped |
|---|---|---|
| Nestlé (Vevey HQ) | SAP SuccessFactors + jobdetails.nestle.com | No public jobs JSON |
| IATA (Geneva HQ) | Custom portal on iata.org | No public jobs JSON |

## Before enabling live ingest

- [ ] Set `INGEST_TEMENOS_LIVE=true`

No account, no key. `TEMENOS_EXTRA_LOCATION_HINTS` is optional (comma-separated
CH/FR place names). Lancy is already in the shared hint list.

## Technical

- Auth: none.
- Search: `POST .../wday/cxs/temenos/Temenoscareers/jobs` (`limit=20`).
- Detail: `GET .../wday/cxs/temenos/Temenoscareers{externalPath}` with
  `Accept: application/json`.
- `external_id`: `temenos-{jobReqId}`.
- Shard is `wd103` (not `wd3`/`wd5`); the shared client takes the shard from the
  public career URL.
- Reuses Richemont JSON fixtures in unit tests (same CXS response shape).

## CLI

```powershell
python -m sentinel_suisse.ingest --provider temenos --live
```

Register the provider once via the admin API before the first run:

```json
{"name":"Temenos","slug":"temenos","base_url":"https://temenos.wd103.myworkdayjobs.com/Temenoscareers","is_active":true}
```

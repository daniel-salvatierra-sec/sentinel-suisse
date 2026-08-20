# STMicroelectronics — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Official,
keyless, no scraping.** Eightfold SmartApply JSON API (same one the career site calls).

## Why this connector exists

STMicroelectronics is headquartered in Plan-les-Ouates (Geneva) and is one of the
canton's largest industrial employers. Careers live at
`stmicroelectronics.eightfold.ai`. The list/detail JSON endpoints are public:

```
GET https://stmicroelectronics.eightfold.ai/api/apply/v2/jobs?domain=stmicroelectronics.com&start=0&num=50
GET https://stmicroelectronics.eightfold.ai/api/apply/v2/jobs/{id}?domain=stmicroelectronics.com
```

~480 open roles globally; typically ~120 in France (Crolles, Grenoble, Rousset, Tours)
and occasional Geneva HQ roles. India/Singapore/US are dropped using the list-level
`location` field *before* any detail call.

## Other Geneva employers checked (not this connector)

| Employer | ATS | Why skipped |
|---|---|---|
| Rolex / JTI / SIG | Oracle Taleo | No public jobs JSON API |
| Pictet / ICRC | SAP SuccessFactors | Legacy portal, no public jobs JSON |
| MSC Cruises | Phenom + SuccessFactors | No keyless jobs JSON |
| dsm-firmenich | Eightfold PCSX | List JSON returns HTTP 403 (`Not authorized for PCSX`) |
| État de Genève | Portal ge.ch | Custom SIRH |
| P&G | Workday (`pg.wd5` / site `1000`) | See `docs/providers/procter-gamble.md` |

## Before enabling live ingest

- [ ] Set `INGEST_STMICROELECTRONICS_LIVE=true`

## CLI

```powershell
python -m sentinel_suisse.ingest --provider stmicroelectronics --live
```

Register once:

```json
{"name":"STMicroelectronics","slug":"stmicroelectronics","base_url":"https://stmicroelectronics.eightfold.ai/careers","is_active":true}
```

# Flatfox — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **Public REST JSON,
no HTML scrape.** Same class as SmartRecruiters / Workday CXS: the endpoints the
Flatfox map itself calls.

## Why this connector exists

Homegate / ImmoScout24 have **no public listing API** for aggregators (SwissRETS is
an *import* gateway for agencies). Flatfox (SMG) exposes keyless JSON:

```
GET https://flatfox.ch/api/v1/pin/?north=&south=&east=&west=
GET https://flatfox.ch/api/v1/public-listing/{pk}/
```

`robots.txt` allows `/`. Apply always goes to the Flatfox listing URL. This is **not**
an Adzuna-style redistribution licence — if SMG objects, turn `INGEST_FLATFOX_LIVE`
off. Partnership email: `docs/outreach/smg-real-estate.md`.

## Before enabling live ingest

- [ ] Set `INGEST_FLATFOX_LIVE=true`
- [ ] Register provider slug `flatfox` once (admin API)
- [ ] Optional: tighten `FLATFOX_NORTH/SOUTH/EAST/WEST` (defaults: Geneva + border)

## Technical

- Pin search geo-filters per region (`FLATFOX_REGIONS`: Geneva, Zurich, Bern,
  Basel, Lausanne, Lugano, Lucerne, St. Gallen, Sion, Fribourg, Neuchatel,
  Winterthur). List search ignores city/bbox and would return 35k ads.
- Skip parking / industrial / CHF < 500 / yearly m² (offices).
- Cap: `FLATFOX_MAX_PER_REGION` (default 30) and `FLATFOX_MAX_LISTINGS` (default 200).
- `listing_type`: always `housing`.
- Fixture for parser tests: `fixtures/flatfox_api_sample.json`

## CLI

```powershell
python -m sentinel_suisse.ingest --provider flatfox --fixture fixtures/flatfox_sample.json
python -m sentinel_suisse.ingest --provider flatfox --live
```

## Limitations

- Public UI never shows the portal name (product rule).
- HTML scrape of Homegate/ImmoScout stays off.

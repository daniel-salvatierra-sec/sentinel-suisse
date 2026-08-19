# France Travail (ex-Pôle Emploi) — legal / technical notes

**Status:** Live connector available (opt-in, disabled by default). **This one uses an
official, documented, free API — not scraping.**

## Why this connector is different

Every other connector in `src/sentinel_suisse/ingest/connectors/` reads a private
site's search page and parses embedded JSON (e.g. `window.__NEXT_DATA__`). That is a
legal grey area: jobs.ch and Homegate explicitly forbid crawling/scraping in their
Terms of Use (checked 2026-08-19).

France Travail (the French public employment service, formerly Pôle Emploi) instead
publishes a real REST API — "API Offres d'emploi v2" — explicitly built for third
parties to build job search apps on top of. From their own developer portal:

> "Pour les plateformes d'emploi et applications mobile : enrichir son catalogue
> d'offres d'emploi." (For job platforms and mobile apps: enrich your job catalog.)

No robots.txt concerns, no ToS conflict — this is the intended, sanctioned use case.

## Before enabling live ingest

- [ ] Create a free account at <https://francetravail.io>
- [ ] Create an "application" in the developer dashboard to get a `client_id` /
      `client_secret`
- [ ] Subscribe the application to the **"Offres d'emploi v2"** API product
- [ ] Set `FRANCE_TRAVAIL_CLIENT_ID` / `FRANCE_TRAVAIL_CLIENT_SECRET` in `.env`
- [ ] Set `INGEST_FRANCE_TRAVAIL_LIVE=true`

## Technical

- Auth: OAuth2 client-credentials grant against
  `https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire`
  (scope `api_offresdemploiv2 o2dsoffre`) — a fresh token is requested on every ingest
  run (tokens are short-lived; no caching needed for a periodic batch job).
- Search: `GET https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search`
  with `Authorization: Bearer <token>`.
- Default filter: `departement=74` (Haute-Savoie, i.e. the Annemasse/Geneva border
  area) — override with `FRANCE_TRAVAIL_DEPARTEMENT`. Optional `FRANCE_TRAVAIL_KEYWORDS`
  maps to the API's `motsCles` parameter.
- `listing_type`: always `job`, `country`: always `FR`.
- `204 No Content` = zero matches for the filter (handled as an empty result, not an
  error). `206 Partial Content` = normal paginated response.
- Fixture: `fixtures/france_travail_sample.json` (raw API response shape, used by the
  connector's own unit tests — not the generic `--fixture` CLI loader).

## CLI

```powershell
# Live (requires FRANCE_TRAVAIL_CLIENT_ID/SECRET + INGEST_FRANCE_TRAVAIL_LIVE=true)
python -m sentinel_suisse.ingest --provider france-travail --live
```

Register the provider once via the admin API before the first run:

```powershell
# {"name":"France Travail","slug":"france-travail","base_url":"https://francetravail.io","is_active":true}
```

## Limitations (MVP)

- Single page per run (`range=0-49`, i.e. up to 50 offers) — no pagination loop yet
- No salary parsing (`price` left `null`); no workload_min/max parsing yet
- Job category comes from `romeLibelle` (France Travail's own job taxonomy), not our
  `job_category` taxonomy — matching against saved-search `job_category` filters may
  need a mapping layer later

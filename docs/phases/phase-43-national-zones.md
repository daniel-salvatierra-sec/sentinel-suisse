# Phase 43 — National Switzerland + DE/IT borders

**Status:** Implemented 2026-08-23  
**Goal:** Treat LinkSwiss as a Swiss product: jobs across major CH cities, and zone chips for the French, German, and Italian borders. Housing stays legal-source only.

## Product

- Zone chips: **Switzerland + borders** | **Switzerland** | **FR border** | **DE border** | **IT border** (5 languages).
- Search aliases for Geneva, Zurich, Bern, Basel, Lausanne, Lugano, and airports (GVA, ZRH, BSL, BRN).
- No Homegate / ImmoScout / newhome / anibis scrape. No paid SMG feeds.

## Ingest (official Adzuna API)

| Slug | Country | Cities |
|------|---------|--------|
| `adzuna` | CH | Geneva, Zurich, Bern, Basel, Lausanne, Lugano |
| `adzuna-fr` | FR | Haute-Savoie + Geneva border towns (existing) |
| `adzuna-de` | DE | Lörrach, Weil am Rhein, Konstanz, Waldshut |
| `adzuna-it` | IT | Como, Varese, Domodossola |

Same `ADZUNA_APP_ID` / `ADZUNA_APP_KEY`. Live flags default off.

## Notes

- `country_code` enum gains `DE` and `IT` (alembic 014).
- Free Adzuna quota: CH multi-city uses more requests per run; DE/IT cron is daily in `deploy/README.md`.
- Housing nationwide is **not** claimed. Direct posts + existing Geneva/FR sources only.

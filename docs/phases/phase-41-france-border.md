# Phase 41 — France border (Leboncoin + Indeed FR)

**Goal:** Cover Geneva border (FR) with fixture-first connectors; add `country` (CH/FR) and a public zone filter. Live ingest remains **disabled by default**.

---

## Providers

| Slug | Type | Country | Fixture |
|------|------|---------|---------|
| `leboncoin` | housing | FR | `fixtures/leboncoin_sample.json` |
| `indeed-fr` | job | FR | `fixtures/indeed_fr_sample.json` |

## Product

- Filter chips: **CH + FR border** | **Switzerland** | **France (border)**
- No portal names in the UI

---

## VPS steps (after deploy)

```bash
cd /opt/sentinel-suisse
docker compose -f docker-compose.prod.yml exec -T api alembic upgrade head

# Register providers (admin Basic auth), then:
docker compose -f docker-compose.prod.yml exec -T api \
  python -m sentinel_suisse.ingest --provider leboncoin --fixture fixtures/leboncoin_sample.json

docker compose -f docker-compose.prod.yml exec -T api \
  python -m sentinel_suisse.ingest --provider indeed-fr --fixture fixtures/indeed_fr_sample.json
```

---

## Deliverables

| Area | Change |
|------|--------|
| Migration | `007_listing_country` |
| Connectors | `leboncoin.py`, `indeed_fr.py` |
| UI | zone chips in `FilterBar` |
| Docs | `docs/providers/{leboncoin,indeed_fr}.md` |
| API version | `0.41.0` |

## Out of scope (later)

- France Travail second job source
- Price/match colour signals + Terminator robot guide
- Direct régie partnerships

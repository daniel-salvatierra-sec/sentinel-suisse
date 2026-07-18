# Phase 40 — More Swiss providers (newhome, anibis, jobup)

**Goal:** Expand CH coverage with fixture-first connectors; live ingest remains **disabled by default**. Public UI still does not advertise portals.

---

## Providers

| Slug | Type | Fixture |
|------|------|---------|
| `newhome` | housing | `fixtures/newhome_sample.json` |
| `anibis` | housing | `fixtures/anibis_sample.json` |
| `jobup` | job | `fixtures/jobup_sample.json` |

---

## VPS / production steps

### 1 — Register providers (once, admin API)

```bash
# From a machine with admin Basic auth against the API, or via curl on the VPS.
# Example payloads:
# {"name":"newhome.ch","slug":"newhome","base_url":"https://www.newhome.ch","is_active":true}
# {"name":"anibis.ch","slug":"anibis","base_url":"https://www.anibis.ch","is_active":true}
# {"name":"jobup.ch","slug":"jobup","base_url":"https://www.jobup.ch","is_active":true}
```

### 2 — Fixture ingest

```bash
docker compose -f docker-compose.prod.yml exec -T api \
  python -m sentinel_suisse.ingest --provider newhome --fixture fixtures/newhome_sample.json

docker compose -f docker-compose.prod.yml exec -T api \
  python -m sentinel_suisse.ingest --provider anibis --fixture fixtures/anibis_sample.json

docker compose -f docker-compose.prod.yml exec -T api \
  python -m sentinel_suisse.ingest --provider jobup --fixture fixtures/jobup_sample.json
```

### 3 — Live ingest

Keep `INGEST_NEWHOME_LIVE`, `INGEST_ANIBIS_LIVE`, `INGEST_JOBUP_LIVE` as `false` until legal checklist in `docs/providers/*.md` is completed.

---

## Deliverables

| Area | Change |
|------|--------|
| Connectors | `newhome.py`, `anibis.py`, `jobup.py` |
| Fixtures | `*_sample.json`, `*_initial_state.json` |
| Config | `INGEST_*_LIVE` + search URLs |
| CLI | wired in `ingest/__main__.py` |
| Tests | `tests/test_*_connector.py` |
| Docs | `docs/providers/{newhome,anibis,jobup}.md` |
| API version | `0.40.0` |

## Out of scope (Phase 41+)

- France border portals (Leboncoin, Indeed FR / France Travail)
- Country/zone filter in public UI
- Enabling live scrape without legal review

# Homegate — legal / technical notes (Phase 3 pilot)

**Status:** Pilot uses local JSON fixture only. Live scraping not enabled yet.

## Before live ingestion

- [ ] Read [Homegate terms of use](https://www.homegate.ch/)
- [ ] Check `robots.txt` at `https://www.homegate.ch/robots.txt`
- [ ] Prefer official API or RSS if available
- [ ] Document decision in this file

## Technical plan (post-approval)

- Identifiable User-Agent with contact email
- Rate limit: configurable via `INGEST_RATE_LIMIT_SECONDS` in `.env`
- No full HTML in logs (PII risk)
- Idempotent upsert via `(provider_id, external_id)` + `content_hash`

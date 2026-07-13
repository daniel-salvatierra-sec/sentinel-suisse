# Privacy & data map (nLPD)

**Status:** Pre-production — privacy policies published (API)  
**Last updated:** 2026-07-13

## Personal data collected

| Field | Table | PII | Encryption at rest | Retention |
|-------|-------|-----|-------------------|-----------|
| `email` | `users` | Yes | Fernet (`PII_ENCRYPTION_KEY`) | Until account deletion |
| `channel_address` | `notification_channels` | Yes (phone/email) | Fernet | Until channel removed |
| `query` | `saved_searches` | Possibly (location keywords) | No | Until search deleted |
| `raw_payload` | `listings` | Possibly (third-party data) | No | TTL 30 days (`maintenance purge-raw-payload`) |

## Non-PII / operational

| Field | Table | Notes |
|-------|-------|-------|
| `content_hash` | `listings` | Deduplication only |
| `external_id` | `listings` | Public provider reference |
| `alerts_log` | — | No message body stored; status + IDs only |

## Legal basis (draft)

- **Alert service:** contract / legitimate interest (user opt-in)
- **Aggregated listings:** public third-party data; link back to source URL

## Before production

- [x] Encrypt `email` and `channel_address` at rest
- [x] Publish privacy policy (FR/DE/ES/PT/EN) — `GET /api/v1/legal/privacy?lang=fr|de|es|pt|en`
- [x] Implement right-to-erasure (delete user cascades channels + searches)
- [x] TTL job for `raw_payload`

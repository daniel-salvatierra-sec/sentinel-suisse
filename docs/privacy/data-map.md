# Privacy & data map (nLPD)

**Status:** Design phase — pre-production  
**Last updated:** 2026-07-10

## Personal data collected

| Field | Table | PII | Encryption at rest | Retention |
|-------|-------|-----|-------------------|-----------|
| `email` | `users` | Yes | Planned (Fernet/KMS) | Until account deletion |
| `channel_address` | `notification_channels` | Yes (phone/email) | Planned | Until channel removed |
| `query` | `saved_searches` | Possibly (location keywords) | No | Until search deleted |
| `raw_payload` | `listings` | Possibly (third-party data) | No | TTL 30 days (planned job) |

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

- [ ] Encrypt `email` and `channel_address` at rest
- [ ] Publish privacy policy (FR/DE per target audience)
- [ ] Implement right-to-erasure (delete user cascades channels + searches)
- [ ] TTL job for `raw_payload`

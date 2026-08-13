# Privacy Policy — Sentinel Suisse

**Version:** 2026-08-13  
**Status:** Personal project / pre-production (draft — legal review before public launch)

## 1. Data controller

Sentinel Suisse (personal project)  
Privacy contact: daninohemyshoping2020@gmail.com

## 2. Personal data collected

| Data | Purpose |
|------|---------|
| Email address | User account, API authentication, email alerts |
| Channel address (email or WhatsApp phone) | Delivering alerts on the chosen channel |
| Saved search criteria | Matching aggregated listings |
| Alert logs (status, timestamp) | Delivery proof, debugging — **no message body stored** |

Aggregated listings come from public third-party sources; we do not store sensitive data in alert bodies.

## 3. Legal basis (nFADP / Swiss nLPD)

- **Alert service:** contract performance / legitimate interest with explicit consent (signup and channel verification).
- **Listing aggregation:** public third-party data; link to the original listing.

## 4. Retention

| Data | Period |
|------|--------|
| Account and channels | Until account deletion |
| Saved searches | Until deleted by the user or with the account |
| Listing `raw_payload` | 30 days maximum (automated maintenance job) |
| Alert logs | Cascade-deleted with the account |

## 5. Security

- Encryption at rest (Fernet) for email and channel addresses.
- Admin passwords hashed (bcrypt); API keys hashed — never stored in plaintext.
- Internal API bound to `127.0.0.1` during development.

## 6. Processors and transfers

Depending on configuration: SMTP provider (e.g. Mailtrap in dev), WhatsApp Cloud API (Meta), database hosting.

**AI assistant (optional feature):** if you use the free-text chat in the guide, your message text (plus the last 6 messages of your conversation, for context) is sent to our AI provider (currently OpenAI, USA) to generate a reply. These messages are **not stored** on our servers after your session (no database history); the AI provider applies its own retention policy. This is a **transfer outside Switzerland/EEA**, covered by the provider's standard contractual clauses. Do not type sensitive information into this chat.

## 7. Your rights

Under the nLPD you have rights of **access**, **rectification**, and **erasure**.

**Account erasure (right to be forgotten):**

```http
DELETE /api/v1/users/me
X-API-Key: <your API key>
```

Deletion is **permanent** and cascade-removes channels, saved searches, and related alert logs.

Requests: daninohemyshoping2020@gmail.com

## 8. Changes

This policy may be updated; version and date appear at the top and via `GET /api/v1/legal/privacy?lang=en`.

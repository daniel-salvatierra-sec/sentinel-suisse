# Business model — open vs paid (Phase 36 → 38)

**Status:** Active product direction (not a legal opinion)  
**Updated:** 2026-07-20

## Decision

| Choice | Status |
|--------|--------|
| **Search (housing + jobs)** | **Always free** — no account required |
| **Alerts** | Freemium stub now → **paid Premium** (Stripe + TWINT) |
| **Source code** | Open / inspectable |
| **Payments** | **Phase B live in code** — enable with Stripe env vars (Checkout + TWINT; PCI via PSP) |

### Why

1. Users explore without obligation; payment only when they want ongoing alerts.
2. Swiss nLPD / Terms must stay clear before charging; Stripe/TWINT handle PCI-DSS — we never store card PANs.
3. Company stack research (Stripe, TWINT, webhooks, Docker/GHA, Sentry, refunds) applies to **alerts billing**, not event ticketing (no pkpass / wallet tickets in LinkSwiss).

## Alert products (Premium)

- Daily **job** alerts  
- **Available** apartments  
- Apartments **under construction** / off-plan (`is_under_construction`)  
- WhatsApp channel + up to 5 saved searches  

**Since 2026-08-19:** search stays free forever, but automatic alert delivery (email or \
WhatsApp) requires Premium. A free account can still save 1 search, but no email/WhatsApp is \
sent for it unless the user upgrades — they must come back and search manually. Users who \
registered before 2026-08-19 keep their pre-existing free email alerts (`users.free_alerts_\
grandfathered`), to avoid cutting off people who already relied on them.

## Payment rails (Phase B)

1. **Stripe Checkout** (CHF) → `POST /api/v1/webhooks/stripe` → `users.is_premium = true`  
2. **TWINT** via `STRIPE_ENABLE_TWINT` + Stripe Dashboard payment methods  
3. Store only `stripe_customer_id` / `stripe_subscription_id` (no PAN)  
4. Refund draft: [`docs/legal/refunds.md`](refunds.md) → `GET /api/v1/legal/refunds`  
5. Optional **Sentry** via `SENTRY_DSN`  
6. Hosting remains **CH/EU** (current VPS)

Do **not** fill live Stripe keys until Terms, privacy contact, and refund text are counsel-reviewed.

## Compliance notes (from enterprise review)

| Topic | LinkSwiss approach |
|-------|-------------------|
| PCI-DSS | Via Stripe (no card data on our servers) |
| nLPD / GDPR | Existing privacy/terms; erasure endpoints |
| Progressive deploy | Docker + compose; migrate then rebuild |
| Refunds | Document before first charge |
| Monitoring | Add Sentry with Phase B payments |

## Out of scope

Billetterie features (signed entry QR, Apple/Google Wallet passes, offline scanners).

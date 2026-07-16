# Business model — open vs paid (Phase 36)

**Status:** Provisional decision for product direction (not a legal opinion)  
**Date:** 2026-07-16

## Decision (recommended)

| Choice | Status |
|--------|--------|
| **Source code** | Open / inspectable (community + portfolio learning) |
| **Core alerts** | Free for end users while pre-production |
| **Funding** | Optional later: sponsorships, donations, or freemium |
| **Payments now** | **Deferred** (Twint / Revolut / crypto wallets → Phase 38+) |

### Why this first

1. Swiss nLPD and Terms must be clear **before** taking money.
2. Integrating Twint/Revolut/crypto early locks you into compliance (merchant KYC, invoicing, refunds) before product-market fit.
3. Open code + free core builds trust for a Swiss housing/job alert tool and still allows later paid tiers (e.g. more channels, higher frequency, team accounts).

## Alternatives considered

| Model | Pros | Cons |
|-------|------|------|
| Fully paid SaaS from day 1 | Clear revenue | Needs payments + stronger legal/tax setup first |
| Closed source + free app | Simpler IP story | Less portfolio/transparency value |
| Donations only | Low friction | Unpredictable; still needs ToS/privacy |

## Funding / aides (Switzerland & open projects)

Possible **later** avenues (research case-by-case; not guarantees):

- Open-source sponsorships (GitHub Sponsors, Liberapay, etc.)
- Local innovation / digital society programmes (cantonal or federal — check eligibility)
- In-kind help (code review, hosting credits) rather than cash

**Paid product** remains valid once Terms, privacy contact, and accounting are ready.

## Payment rails (future phase)

When ready, evaluate in this order for CH users:

1. **Twint** — local ubiquity  
2. **Card / Revolut Business** (or similar PSP) — EU/CH cards  
3. **Crypto wallets** — optional niche; higher AML/compliance burden  

Do **not** wire payment APIs until this document is updated to “Active”.

## User confirmation

Confirm or override this provisional decision before Phase 38 (payments).

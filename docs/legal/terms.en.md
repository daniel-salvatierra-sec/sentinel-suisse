# Terms of Service — Sentinel Suisse

**Version:** 2026-07-16  
**Status:** Draft — legal review recommended before public launch  
**Governing law:** Switzerland (Swiss Federal Act on Data Protection — nFADP / nLPD)

## 1. Service

Sentinel Suisse (“the Service”) aggregates publicly available housing and job listings and sends optional alerts (email / WhatsApp) according to criteria you save.

The Service is a **personal / pre-production project**. Availability is not guaranteed.

## 2. Acceptance

By creating an account, using the public search UI, or enabling alerts, you confirm that you have read:

- these Terms of Service, and  
- the [Privacy Policy](/api/v1/legal/privacy?lang=en)

and that you accept them.

## 3. Eligibility and account

- You must provide accurate contact details for channels you enable.
- You are responsible for keeping your API key confidential.
- You may delete your account at any time (`DELETE /api/v1/users/me`).

## 4. Acceptable use

You agree **not** to:

- abuse rate limits, scrape internal APIs, or attempt unauthorized access;
- use alerts for unlawful harassment or spam;
- redistribute listing content in ways that violate third-party portal terms;
- reverse-engineer or overload the Service.

We may suspend accounts that violate these rules.

## 5. Third-party listings

Listings come from external portals (e.g. Homegate, Flatfox, ImmoScout24, jobs.ch). We are **not** the landlord, employer, or publisher. Always verify offers on the original source URL. We do not guarantee accuracy or availability of third-party data.

## 6. Alerts and notifications

- Alerts depend on ingestion, matching, and optional channels (SMTP, WhatsApp Cloud API).
- Delivery is **best effort**; delays or failures may occur.
- You can disable channels or erase your data at any time.

## 7. Privacy

Personal data is processed under Swiss nLPD as described in the Privacy Policy. Summary: encryption at rest for emails/phones, right to erasure, limited retention of raw listing payloads.

## 8. Open source and funding (current intent)

- Source code is intended to remain **inspectable / open** for learning and community review.
- Core alert features are intended to remain **free** for personal use while the project is pre-production.
- Optional **paid plans, sponsorships, or donations** (e.g. Twint, Revolut, crypto) may be introduced later; they are **not active** until a dedicated payment phase and updated Terms are published.

## 9. Disclaimer

THE SERVICE IS PROVIDED “AS IS” WITHOUT WARRANTIES OF ANY KIND. To the extent permitted by Swiss law, we are not liable for indirect damages, lost opportunities (missed flats/jobs), or third-party outages.

## 10. Changes

We may update these Terms. The `version` date in this document and the API response will change. Continued use after publication constitutes acceptance of material updates when notified in-app or by email where feasible.

## 11. Contact

Legal / privacy contact: privacy@sentinel-suisse.example *(replace before production)*

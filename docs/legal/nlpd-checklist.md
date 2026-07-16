# nLPD / nFADP operational checklist

**Companion to:** [`data-map.md`](../privacy/data-map.md), privacy policies, Terms of Service  
**Updated:** 2026-07-16 (Phase 36)

## Already in place

- [x] Data map of PII fields and retention
- [x] Encryption at rest for email / channel addresses
- [x] Privacy policy published (5 languages) via API
- [x] Right to erasure (`DELETE /api/v1/users/me`)
- [x] Raw listing payload TTL
- [x] Terms of Service draft (5 languages) via API
- [x] Consent at signup (privacy; Terms referenced in UI)

## Before public production launch

- [ ] Replace `privacy@sentinel-suisse.example` with a real contact
- [ ] Legal review of Privacy Policy + Terms (Swiss counsel or qualified advisor)
- [ ] Confirm hosting region (prefer CH/EEA) and document processors (SMTP, Meta WhatsApp, DB host)
- [ ] Cookie / tracker policy if any analytics are added (currently none intended)
- [ ] Document lawful basis per processing purpose in final privacy text
- [ ] Process for access / rectification requests (beyond self-service erasure)
- [ ] Incident response note (who to notify if a breach of personal data)

## If / when taking payments

- [ ] Update Terms + Privacy for billing data
- [ ] Choose PSP (Twint / card / other) and sign DPA where required
- [ ] Invoicing / VAT assessment for your situation
- [ ] Do **not** store full card numbers in our DB

## Open source

- [ ] Choose and publish a LICENSE file when opening the repo publicly
- [ ] Keep secrets out of git (existing `.env` / gitleaks practice)

## Notes

This checklist is an **engineering/ops aid**, not legal advice. Swiss nLPD obligations depend on your role as controller and on whether the Service is offered to individuals in Switzerland.

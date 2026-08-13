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

- [x] Replace `privacy@sentinel-suisse.example` with a real contact (daninohemyshoping2020@gmail.com, 2026-08-13)
- [ ] Legal review of Privacy Policy + Terms (Swiss counsel or qualified advisor)
- [ ] Confirm hosting region (prefer CH/EEA) and document processors (SMTP, Meta WhatsApp, DB host)
- [ ] Cookie / tracker policy if any analytics are added (currently none intended)
- [ ] Document lawful basis per processing purpose in final privacy text
- [ ] Process for access / rectification requests (beyond self-service erasure)
- [ ] Incident response note (who to notify if a breach of personal data)

## If / when taking payments

- [x] Update Terms + Privacy for billing data (contact email + live Premium plan description, 2026-08-13)
- [ ] Choose PSP (Twint / card / other) and sign DPA where required
- [ ] **Swiss MWST**: only mandatory once global turnover exceeds **CHF 100,000/year** (Art. 10 VAT Act). Below that, registration is optional.
- [ ] **EU/French VAT (TVA)**: **no minimum threshold** for a non-EU business selling digital services to EU consumers — liability starts from the **first** sale to a French/EU-resident subscriber. Confirm with an accountant whether any current subscriber is billed from France/EU and, if so, register for the **Non-Union OSS** scheme promptly.
- [ ] Do **not** store full card numbers in our DB

## If / when serving users in France or the EU

- [ ] Confirm GDPR applies in parallel with the nLPD for French/EU users (Art. 3(2) GDPR) — Swiss adequacy only covers EU→CH transfers, not the reverse
- [ ] Get counsel's view on whether a GDPR Art. 27 EU representative is required
- [ ] Add a "Mentions légales / Legal Notice" page (legal entity name, form, address, UID, VAT number once registered) — also closes the Swiss UWG Art. 3(1)(s) e-commerce disclosure gap
- [ ] Have counsel review the refund policy's "not yet used" condition against French droit de rétractation (Code de la consommation Art. L221-18/L221-28)

## Open source

- [ ] Choose and publish a LICENSE file when opening the repo publicly
- [ ] Keep secrets out of git (existing `.env` / gitleaks practice)

## Notes

This checklist is an **engineering/ops aid**, not legal advice. Swiss nLPD obligations depend on your role as controller and on whether the Service is offered to individuals in Switzerland.

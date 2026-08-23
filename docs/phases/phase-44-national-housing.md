# Phase 44 — National housing via Flatfox boxes

**Status:** Implemented 2026-08-23  
**Goal:** Show rentals beyond Geneva using only Flatfox's public pin API. No Homegate / ImmoScout / newhome / anibis scrape.

## What changed

- Flatfox walks named city boxes (Zurich, Bern, Basel, Lausanne, Lugano, …).
- Locations keep the real city (no more ", Geneva" suffix on every CH ad).
- Caps: 30 details per region, 200 total, so one run stays shorter than a full Adzuna sweep.

## Notes

- This is still Flatfox inventory, not every Swiss portal.
- Direct landlord posts remain the other legal housing source.
- Turn off `INGEST_FLATFOX_LIVE` if SMG objects.

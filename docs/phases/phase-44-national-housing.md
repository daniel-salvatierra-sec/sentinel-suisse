# Phase 44 — National housing via Flatfox boxes

**Status:** Implemented 2026-08-23  
**Goal:** Show rentals beyond Geneva using only Flatfox's public pin API. No Homegate / ImmoScout / newhome / anibis scrape.

## What changed

- Flatfox walks named city boxes (Zurich, Bern, Basel, Lausanne, Lugano, … plus
  the same extra towns as the job crawl, and FR/DE/IT border boxes).
- Locations keep the real city (no more ", Geneva" suffix on every CH ad).
- Caps: 50 details per region, 2500 total. Each box prefers high-rent pins first
  so 4–5 room homes are not drowned by the first 25 map pins.

## Notes

- This is still Flatfox inventory, not every Swiss portal.
- Direct landlord posts remain the other legal housing source.
- Turn off `INGEST_FLATFOX_LIVE` if SMG objects.

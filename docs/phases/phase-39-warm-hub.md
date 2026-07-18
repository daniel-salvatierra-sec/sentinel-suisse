# Phase 39 — Warm alpine hub (Home / Work)

**Goal:** Present LinkSwiss hub as a **modern full-bleed illustration**: effort/climb at Work (bottom) → home/stability at Home (top), matching the “hombre subiendo” narrative (not flat SVG placeholders).

**Asset:** `frontend/public/hub/hero.png`

## Check

```powershell
cd frontend
npm run dev
```

Open http://127.0.0.1:5173 — or after deploy: https://linkswiss.ch

1. Brand **LinkSwiss** reads as hero.
2. Home (top) feels arrival / keys / daylight.
3. Work (bottom) feels climb / city effort / CV hint.
4. Soft cloud accent (future Vacaciones), not a third panel.
5. Active zone expands with light motion.

## Deliverables

| Area | Change |
|------|--------|
| UI | `GoalHub.tsx` art layers + copy stack |
| CSS | Warm lake/sun/clay palette, zone gradients, SVG atmospheres |
| Versions | `0.39.0` |

## Out of scope

- Real photo assets / Excalidraw export pipeline
- Vacaciones as selectable zone
- CV upload flow

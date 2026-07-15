# Phase 22 — QR scan-to-subscribe

**Branch:** `feature/phase-22-qr-subscribe`  
**Goal:** Show a QR deep link (and copyable URL) that opens Compte signup with language, category and search prefills.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-22-qr-subscribe
```

### Step 2 — Install QR dependency

```powershell
cd frontend
npm install
```

### Step 3 — Run UI (API optional for QR alone)

```powershell
npm run dev
```

Open **http://127.0.0.1:5173** → tab **Compte** (logged out) or **Alertes** without session.  
You should see the QR + “Copy link”.

Optional deep-link check (same machine):

```
http://127.0.0.1:5173/?tab=account&lang=es&type=job&q=Geneva
```

Should open Compte, language ES, category Emploi, search Geneva.

### Step 4 — Phone on LAN (optional)

Same Wi‑Fi as PC; Vite already binds `127.0.0.1` only. For phone scan, either:

1. Temporarily set Vite `server.host` / use host IP, **or**
2. Create `frontend/.env.local`:

```
VITE_PUBLIC_APP_URL=http://YOUR_LAN_IP:5173
```

Restart `npm run dev`. Restart after hosting with HTTPS URL.

### Step 5 — Tests

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **63 passed** (1 tiny deep-link shape test; QR UI is frontend).

### Step 6 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add QR scan-to-subscribe deep links (Phase 22)"
git checkout main
git merge feature/phase-22-qr-subscribe
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Link builder | `frontend/src/subscribeLink.ts` |
| UI | `SubscribeQr.tsx` on Compte signup + Alertes (no session) |
| Deep link | `App.tsx` reads `tab`, `lang`, `type`, `q` |
| i18n | 5 languages (`qrTitle`, `qrDesc`, `qrCopy`, `qrCopied`) |
| Deps | `qrcode` + `@types/qrcode` |
| CSS | Fixed broken `.lang-bar` / QR placeholder; `.subscribe-qr` |
| Versions | API `0.22.0`, frontend `0.22.0` |

## Out of scope (Phase 23+)

- Meta WhatsApp webhook (needs public HTTPS)
- Public signup in production
- Hosting / TLS termination

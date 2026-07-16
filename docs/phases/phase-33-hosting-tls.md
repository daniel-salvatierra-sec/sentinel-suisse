# Phase 33 — Hosting + TLS (Docker + Caddy)

**Branch:** `feature/phase-33-hosting-tls`  
**Goal:** Production Docker stack with Caddy HTTPS, trusted hosts, and deployment docs.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-33-hosting-tls
```

### Step 2 — Tests

```powershell
$secure = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$env:TEST_ADMIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
pytest -q
```

Expect **82+ passed** (`test_health`, `test_trusted_hosts`).

### Step 3 — Local Docker smoke test (optional but recommended)

```powershell
Copy-Item .env.production.example .env
```

Edit `.env`: set `POSTGRES_PASSWORD`, `SECRET_KEY`, `PII_ENCRYPTION_KEY`, `ADMIN_PASSWORD_HASH`, and for local test:

```
DOMAIN=localhost
PUBLIC_APP_URL=https://localhost
TRUSTED_HOSTS=localhost
```

Then:

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

Open **https://localhost/health** (accept cert warning). Stop when done:

```powershell
docker compose -f docker-compose.prod.yml down
```

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: add Docker production stack with Caddy TLS (Phase 33)"
git checkout main
git merge feature/phase-33-hosting-tls
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Docker | `Dockerfile` (API + built frontend) |
| Compose | `docker-compose.prod.yml` (postgres, redis, api, caddy) |
| TLS | `deploy/Caddyfile` — Let's Encrypt or localhost internal |
| Config | `TRUSTED_HOSTS`, `.env.production.example` |
| API | `create_app()`, TrustedHost middleware, `/health` |
| Docs | `deploy/README.md` |
| Versions | `0.33.0` |

## When you pick a real VPS

See [`deploy/README.md`](../deploy/README.md) — DNS A record, ports 80/443, fill production `.env`.

## Out of scope

- Managed PaaS one-click (Fly.io/Railway) — use this stack or adapt later
- CI/CD pipeline to VPS

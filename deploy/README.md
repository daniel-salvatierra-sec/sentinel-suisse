# Hosting / production deployment

Docker Compose stack with **Caddy** for automatic HTTPS (Let's Encrypt).

## Quick smoke test (localhost)

1. Copy `.env.production.example` → `.env`
2. Set at minimum:
   - `POSTGRES_PASSWORD` (strong random)
   - `SECRET_KEY`, `PII_ENCRYPTION_KEY`, `ADMIN_PASSWORD_HASH`
   - `DOMAIN=localhost`
   - `PUBLIC_APP_URL=https://localhost`
   - `TRUSTED_HOSTS=localhost`
3. Build and start:

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

4. Open **https://localhost** (accept Caddy internal certificate warning)
5. Check API: `https://localhost/health` → `{"status":"ok","env":"production"}`

Stop:

```powershell
docker compose -f docker-compose.prod.yml down
```

## Real domain (VPS)

Recommended: small VPS (Hetzner, Infomaniak, etc.) with Docker.

1. Point DNS **A** record for your domain → server IP
2. In `.env`:
   - `DOMAIN=your-domain.example`
   - `PUBLIC_APP_URL=https://your-domain.example`
   - `TRUSTED_HOSTS=your-domain.example`
   - `PUBLIC_SEARCH_ENABLED=true`, `PUBLIC_SIGNUP_ENABLED=true`
   - `SIGNUP_AUTO_VERIFY=false`
3. Open firewall ports **80** and **443**
4. `docker compose -f docker-compose.prod.yml up -d --build`
5. Caddy obtains Let's Encrypt certificates automatically

## Meta WhatsApp webhook

After HTTPS is live:

```
https://your-domain.example/api/v1/webhooks/whatsapp
```

Set `WHATSAPP_VERIFY_TOKEN` and `WHATSAPP_APP_SECRET` in `.env` to match Meta app settings.

## Architecture

```
Internet → Caddy (:443 TLS) → api:8000 (FastAPI + static frontend)
                ↓
         postgres / redis (internal network only)
```

## Security notes

- Postgres/Redis are **not** exposed on host ports in production compose
- Uvicorn runs with `--proxy-headers` behind Caddy
- Set `TRUSTED_HOSTS` to your public hostname(s)
- Swagger `/docs` is disabled when `APP_ENV=production`
- Never commit `.env` with real secrets
- Container logs rotate via `json-file` (`max-size: 10m`, `max-file: 3`)

## Production hardening (Phase 35)

Run these **once on the VPS** (Linux):

| Script | Purpose |
|--------|---------|
| `deploy/setup-firewall.sh` | UFW: allow SSH + 80/443 only |
| `deploy/fail2ban/sshd.local` | Copy to `/etc/fail2ban/jail.d/`, restart fail2ban |
| `deploy/backup-db.sh` | Postgres dump → `./backups/` (14-day retention) |
| `deploy/restore-db.sh` | Restore from `.sql.gz` backup |
| `deploy/monitor-health.sh` | Exit non-zero if `/health` or DB check fails |

Example cron on VPS:

```bash
0 3 * * * /opt/sentinel-suisse/deploy/backup-db.sh
*/5 * * * * /opt/sentinel-suisse/deploy/monitor-health.sh https://your-domain.example/health
```

`/health` returns `database: ok` when Postgres is reachable; HTTP **503** when not.

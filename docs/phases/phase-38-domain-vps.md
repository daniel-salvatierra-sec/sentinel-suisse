# Phase 38 — LinkSwiss brand + domain + VPS

**Branch:** `feature/phase-38-linkswiss-vps`  
**Goal:** Single brand **LinkSwiss** (UI + emails), public hostname **linkswiss.ch**, wire existing Hetzner VPS (Docker + DNS + GitHub deploy secrets).

**Confirmed (user, 2026-07):**

| Check | Result |
|-------|--------|
| WHOIS `linkswiss.ch` | Not registered (available) |
| Swissreg `LinkSwiss` | 0 hits |
| VPS | Hetzner already paid (~CHF 6/mo) |
| SSH key | `~/.ssh/linkswiss_ed25519` created on Windows |

---

## Your steps (run in order)

### Step 1 — Register domain

1. Buy **linkswiss.ch** at a .ch registrar (Hostpoint, Infomaniak, etc.).
2. Keep registrar login under your control.

### Step 2 — Attach SSH key to Hetzner + get IP

1. [Hetzner Console](https://console.hetzner.cloud/) → your project → **Security → SSH Keys** → add public key if missing:

```powershell
Get-Content "$env:USERPROFILE\.ssh\linkswiss_ed25519.pub"
```

2. Open your existing server → note **IPv4**.
3. If the server was created without this key, add the key in Hetzner and/or paste the public key into `~/.ssh/authorized_keys` via the Hetzner console/rescue.

Test (replace IP):

```powershell
ssh -i "$env:USERPROFILE\.ssh\linkswiss_ed25519" root@YOUR_VPS_IP
```

### Step 3 — DNS A record

At the registrar for **linkswiss.ch**:

| Type | Name | Value |
|------|------|-------|
| A | `@` | your VPS IPv4 |
| A | `www` | same IP (optional) |

```powershell
Resolve-DnsName linkswiss.ch -Type A
```

### Step 4 — Bootstrap VPS (Docker + repo)

On the VPS (SSH), one block at a time:

```bash
apt-get update && apt-get upgrade -y
```

```bash
apt-get install -y ca-certificates curl git ufw fail2ban
```

```bash
curl -fsSL https://get.docker.com | sh
```

```bash
mkdir -p /opt/sentinel-suisse
cd /opt/sentinel-suisse
git clone https://github.com/daniel-salvatierra-sec/sentinel-suisse.git .
```

```bash
cp .env.production.example .env
nano .env
```

Minimum:

```env
APP_ENV=production
DOMAIN=linkswiss.ch
PUBLIC_APP_URL=https://linkswiss.ch
TRUSTED_HOSTS=linkswiss.ch,www.linkswiss.ch
POSTGRES_PASSWORD=<strong-random>
SECRET_KEY=<strong-random>
PII_ENCRYPTION_KEY=<fernet-key>
ADMIN_PASSWORD_HASH=<hash>
PUBLIC_SEARCH_ENABLED=true
PUBLIC_SIGNUP_ENABLED=true
SIGNUP_AUTO_VERIFY=false
```

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

```bash
curl -sS https://linkswiss.ch/health
```

### Step 5 — Hardening

```bash
cd /opt/sentinel-suisse
chmod +x deploy/*.sh
./deploy/setup-firewall.sh
cp deploy/fail2ban/sshd.local /etc/fail2ban/jail.d/
systemctl restart fail2ban
```

Cron: see [`deploy/README.md`](../../deploy/README.md) with `https://linkswiss.ch/health`.

### Step 6 — GitHub Actions secrets

| Secret | Value |
|--------|--------|
| `SSH_HOST` | VPS IPv4 |
| `SSH_USER` | `root` (or your user) |
| `SSH_PRIVATE_KEY` | private key `linkswiss_ed25519` |
| `DEPLOY_PATH` | `/opt/sentinel-suisse` |
| `SSH_PORT` | `22` (optional) |

### Step 7 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: rebrand to LinkSwiss and Phase 38 VPS checklist"
git checkout main
git merge feature/phase-38-linkswiss-vps
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| Brand | UI + verification emails → **LinkSwiss** |
| Domain | Checklist for **linkswiss.ch** |
| VPS | Hetzner existing server → Docker / Caddy / CI-CD |
| Versions | `0.38.0` |

## Out of scope

- Trademark filing (swissreg clear for now; lawyer later)
- Off-site backups
- WhatsApp Meta webhook go-live
- Payments

---

## Resume later — CI/CD status (2026-07-18)

**Live site:** https://linkswiss.ch (Docker + Caddy TLS + UFW OK).

**GitHub Actions secrets (set):** `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY` (use `~/.ssh/linkswiss_github_deploy` **without** passphrase), `DEPLOY_PATH=/opt/sentinel-suisse`. Do **not** keep `SSH_PASSPHRASE` for the deploy key.

**Personal SSH (Windows):** `linkswiss_ed25519` (passphrase) — daily use.  
**CI SSH:** `linkswiss_github_deploy` — tested OK with `OK-DEPLOY-KEY`.

**Last Deploy to VPS failure (after SSH worked):**

```text
M deploy/backup-db.sh
M deploy/docker-entrypoint.sh
M deploy/monitor-health.sh
M deploy/restore-db.sh
M deploy/setup-firewall.sh
Already up to date.
Process exited with status 1
```

Likely causes to fix next session:

1. **Dirty tree on VPS** under `/opt/sentinel-suisse` (local mods / CRLF on `deploy/*.sh`) blocking a clean checkout/pull path or confusing the script.
2. **`docker compose` step** may have exited 1 with little log — re-run with more logging.

**Next commands on VPS (when resuming):**

```bash
cd /opt/sentinel-suisse
git status
git checkout -- deploy/
git pull --ff-only origin main
docker compose -f docker-compose.prod.yml up -d --build
curl -sS https://linkswiss.ch/health; echo
```

Then **Re-run** Actions → Deploy to VPS, or push a tiny docs commit to `main`.

Optional workflow harden: before `git pull`, add `git reset --hard origin/main` (only if no uncommitted work should be kept on the VPS — `.env` is untracked and safe).

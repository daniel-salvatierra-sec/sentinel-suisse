# Phase 35 — Production hardening

**Branch:** `feature/phase-35-prod-hardening`  
**Goal:** Backups, firewall, fail2ban, log rotation, and deep `/health` for VPS monitoring.

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-35-prod-hardening
```

### Step 2 — Tests

```powershell
$secure = Read-Host "Contraseña admin" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$env:TEST_ADMIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
pytest -q
```

Expect **84+ passed** (deep health + 503 when DB down).

Local health check (with uvicorn running):

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

Expect `database: ok` and `status: ok`.

### Step 3 — VPS hardening (when you have a server)

SSH into the VPS, then:

```bash
cd /opt/sentinel-suisse
sudo chmod +x deploy/*.sh
sudo ./deploy/setup-firewall.sh
sudo cp deploy/fail2ban/sshd.local /etc/fail2ban/jail.d/
sudo systemctl restart fail2ban
./deploy/backup-db.sh
./deploy/monitor-health.sh https://your-domain.example/health
```

Add cron (see `deploy/README.md`).

### Step 4 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: production hardening backups firewall monitoring (Phase 35)"
git checkout main
git merge feature/phase-35-prod-hardening
git push origin main
```

---

## Deliverables

| Area | Change |
|------|--------|
| API | `/health` includes `database` status; 503 when DB unreachable |
| Scripts | `backup-db.sh`, `restore-db.sh`, `setup-firewall.sh`, `monitor-health.sh` |
| fail2ban | `deploy/fail2ban/sshd.local` |
| Compose | Log rotation on all prod services |
| Versions | `0.35.0` |

## Out of scope

- Off-site backup storage (S3, Backblaze)
- Full observability stack (Grafana/Prometheus)

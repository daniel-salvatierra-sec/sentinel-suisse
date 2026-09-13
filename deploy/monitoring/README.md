# LinkSwiss monitoring (Wazuh + Grafana)

Minimal pack for the Infomaniak VPS (`linkswiss.ch`). Import these on your
**monitoring host** (not on the honeypot). Keep the Oracle honeypot isolated.

## What you get

| Tool | File | Purpose |
|------|------|---------|
| Wazuh agent | `wazuh/ossec.conf.snippet` | FIM on `.env` / compose / Caddy + Docker logs |
| Wazuh manager | `wazuh/local_rules.xml` | Alerts when those files change or containers die |
| Grafana | `grafana/linkswiss-dashboard.json` | Health + uptime panel (Infinity / JSON) |
| Grafana | `grafana/contact-points.md` | What to alert on |
| Probe | `../monitor-health.sh` | Already in deploy — cron every 5 min |

## 1) Wazuh (agent on LinkSwiss VPS)

1. Install the Wazuh agent on `84.234.31.127` pointing to your manager.
2. Merge `wazuh/ossec.conf.snippet` into `/var/ossec/etc/ossec.conf` (or use agent groups).
3. Copy `wazuh/local_rules.xml` rules into the **manager** (`/var/ossec/etc/rules/local_rules.xml`) and restart the manager.
4. Restart the agent: `systemctl restart wazuh-agent`.

Expect alerts when:
- `.env`, `Caddyfile`, or `docker-compose.prod.yml` change
- Docker reports a container stopped / unhealthy
- SSH authentication failures spike (complements fail2ban)

## 2) Grafana

1. Install the **Infinity** datasource plugin (or use any JSON/HTTP datasource).
2. Create a datasource that GETs `https://linkswiss.ch/health` every 60s.
3. Import `grafana/linkswiss-dashboard.json`.
4. Add alert rules from `grafana/contact-points.md` (email / Telegram / WhatsApp webhook).

Optional stronger stack on the monitoring host:
- Prometheus + blackbox_exporter probing `https://linkswiss.ch/health`
- node_exporter on the VPS (scrape only from the monitoring host firewall)

## 3) Keep the existing watchdog

On the VPS cron (already documented in `deploy/README.md`):

```bash
*/5 * * * * /opt/sentinel-suisse/deploy/run-watchdog.sh
```

That covers app down / DB down / stale ingest even if Grafana is offline.

## Do not

- Do not install Wazuh manager on the same box as production if you can avoid it
- Do not point OpenVAS aggressive authenticated scans at live Postgres
- Do not share the honeypot network with LinkSwiss

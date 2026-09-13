# Grafana alerts — LinkSwiss

Create these after importing the dashboard. Contact point: your email / Telegram.

## Alert A — App down

- **Query:** Infinity → `https://linkswiss.ch/health` → field `status`
- **Condition:** `status` != `ok` for **2m**
- **Severity:** critical
- **Action:** page yourself; on VPS run:
  - `docker compose -f /opt/sentinel-suisse/docker-compose.prod.yml ps`
  - `docker compose -f /opt/sentinel-suisse/docker-compose.prod.yml logs api --tail 80`

## Alert B — Database down

- **Query:** same endpoint → field `database`
- **Condition:** `database` != `ok` for **2m**
- **Severity:** critical
- **Action:** check Postgres container health + disk

## Alert C — Disk / host (from node_exporter or Wazuh)

- **Condition:** root filesystem ≥ **90%** for **5m**
- **Severity:** high
- **Action:** prune Docker images, rotate logs, check backup growth

## Alert D — Optional TLS

- Probe `https://linkswiss.ch` certificate expiry **< 14 days**
- Caddy renews automatically; alert only if renewal stuck

## Note

Keep `deploy/run-watchdog.sh` on the VPS even with Grafana. It is the last line if the monitoring host itself is down.

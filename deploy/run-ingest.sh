#!/bin/sh
# Run a live ingest connector inside the running api container (cron-friendly).
# Usage: ./deploy/run-ingest.sh <provider-slug>
# Cron example (hourly): 0 * * * * /opt/sentinel-suisse/deploy/run-ingest.sh adzuna >> /var/log/linkswiss-ingest.log 2>&1

set -e
cd "$(dirname "$0")/.."

PROVIDER="${1:?Usage: run-ingest.sh <provider-slug> (e.g. adzuna, france-travail)}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose -f $COMPOSE_FILE"
else
  COMPOSE="docker compose -f $COMPOSE_FILE"
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Ingesting provider=$PROVIDER"
$COMPOSE exec -T api python -m sentinel_suisse.ingest --provider "$PROVIDER" --live --dispatch-alerts

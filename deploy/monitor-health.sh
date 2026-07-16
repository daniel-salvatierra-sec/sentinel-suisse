#!/bin/sh
# External health probe — exit 0 when app + DB are healthy.
# Usage: ./deploy/monitor-health.sh https://your-domain.example/health
# Cron example (every 5 min): */5 * * * * /opt/sentinel-suisse/deploy/monitor-health.sh https://example.com/health

set -e

URL="${1:-https://localhost/health}"
BODY="$(curl -fsS "$URL")"

echo "$BODY" | grep -q '"status":"ok"' || {
  echo "Health check failed: $BODY"
  exit 1
}

echo "$BODY" | grep -q '"database":"ok"' || {
  echo "Database check failed: $BODY"
  exit 1
}

echo "OK: $URL"

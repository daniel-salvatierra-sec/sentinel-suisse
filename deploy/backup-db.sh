#!/bin/sh
# Daily Postgres backup for production Docker stack.
# Usage: ./deploy/backup-db.sh
# Cron example (03:00 daily): 0 3 * * * /opt/sentinel-suisse/deploy/backup-db.sh

set -e
cd "$(dirname "$0")/.."

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT="$BACKUP_DIR/sentinel_suisse_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose -f $COMPOSE_FILE"
else
  COMPOSE="docker compose -f $COMPOSE_FILE"
fi

$COMPOSE exec -T postgres pg_dump -U sentinel sentinel_suisse | gzip > "$OUTPUT"
echo "Backup written: $OUTPUT"

find "$BACKUP_DIR" -name "sentinel_suisse_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

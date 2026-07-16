#!/bin/sh
# Restore Postgres from a gzip SQL dump created by backup-db.sh.
# Usage: ./deploy/restore-db.sh backups/sentinel_suisse_YYYYMMDD_HHMMSS.sql.gz

set -e
cd "$(dirname "$0")/.."

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <backup.sql.gz>"
  exit 1
fi

BACKUP_FILE="$1"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose -f $COMPOSE_FILE"
else
  COMPOSE="docker compose -f $COMPOSE_FILE"
fi

echo "Restoring from $BACKUP_FILE (this replaces current DB contents)."
gunzip -c "$BACKUP_FILE" | $COMPOSE exec -T postgres psql -U sentinel -d sentinel_suisse
echo "Restore complete."

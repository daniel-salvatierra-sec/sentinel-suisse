#!/bin/sh
set -e
cd /app
alembic upgrade head
exec uvicorn sentinel_suisse.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --proxy-headers \
    --forwarded-allow-ips='*'

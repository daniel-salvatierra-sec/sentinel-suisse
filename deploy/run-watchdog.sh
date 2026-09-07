#!/bin/sh
# Cron: */5 * * * * /opt/sentinel-suisse/deploy/run-watchdog.sh >> /var/log/linkswiss-watchdog.log 2>&1
cd "$(dirname "$0")/.."
exec python3 deploy/watchdog.py

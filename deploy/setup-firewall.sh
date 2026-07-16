#!/bin/sh
# UFW baseline for VPS: SSH + HTTP + HTTPS only.
# Run once on the VPS as root: sudo ./deploy/setup-firewall.sh

set -e

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root (sudo $0)"
  exit 1
fi

if ! command -v ufw >/dev/null 2>&1; then
  echo "ufw not installed. On Debian/Ubuntu: apt install ufw"
  exit 1
fi

ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status verbose

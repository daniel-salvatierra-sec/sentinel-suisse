#!/bin/bash
# Append an IPv4 to linkswiss-bad-ips and reload Wazuh manager.
# Usage: sudo ./add-bad-ip.sh 203.0.113.50

set -euo pipefail

LIST="/var/ossec/etc/lists/linkswiss-bad-ips"
IP="${1:-}"

if [[ -z "$IP" ]]; then
  echo "Usage: sudo $0 <ipv4>"
  exit 1
fi

if ! [[ "$IP" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
  echo "Invalid IPv4: $IP"
  exit 1
fi

NEVER=(
  "63.178.67.83"
  "100.82.114.60"
  "100.95.7.14"
  "127.0.0.1"
)
for blocked in "${NEVER[@]}"; do
  if [[ "$IP" == "$blocked" ]]; then
    echo "Refusing to blacklist protected IP: $IP"
    exit 1
  fi
done

if [[ ! -f "$LIST" ]]; then
  touch "$LIST"
  chown root:wazuh "$LIST"
  chmod 640 "$LIST"
fi

if grep -qE "^${IP}:" "$LIST"; then
  echo "Already listed: $IP"
  exit 0
fi

echo "${IP}:" >>"$LIST"
echo "Added ${IP}: to $LIST"

if [[ -x /var/ossec/bin/wazuh-makelists ]]; then
  /var/ossec/bin/wazuh-makelists
elif [[ -x /var/ossec/bin/ossec-makelists ]]; then
  /var/ossec/bin/ossec-makelists
fi

if systemctl is-active --quiet wazuh-manager; then
  systemctl restart wazuh-manager
  echo "wazuh-manager restarted"
fi

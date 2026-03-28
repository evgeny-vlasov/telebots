#!/usr/bin/env bash
# scripts/status.sh — show status of all telebots services
echo "=== Telebots Services ==="
for svc in $(systemctl list-units --type=service --all | grep 'telebots-' | awk '{print $1}'); do
    echo ""
    echo "── $svc"
    systemctl status "$svc" --no-pager -l | tail -5
done

echo ""
echo "=== Listening Ports ==="
ss -tlnp | grep -E ':(501[0-9])' || echo "(none found in 5010-5019)"

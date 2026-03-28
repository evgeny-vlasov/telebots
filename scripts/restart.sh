#!/usr/bin/env bash
# scripts/restart.sh [botname]
# Restart one bot, or all telebots services if no arg given.
if [ -n "$1" ]; then
    SVC="telebots-${1}.service"
    echo "Restarting $SVC..."
    sudo systemctl restart "$SVC"
    sudo systemctl status "$SVC" --no-pager -l | tail -8
else
    echo "Restarting all telebots services..."
    for svc in $(systemctl list-units --type=service --all | grep 'telebots-' | awk '{print $1}'); do
        echo "  → $svc"
        sudo systemctl restart "$svc"
    done
    echo "Done."
fi

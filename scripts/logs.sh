#!/usr/bin/env bash
# scripts/logs.sh <botname> [lines]
# Usage: ./scripts/logs.sh anglers
#        ./scripts/logs.sh anglers 100
BOT=${1:?"Usage: $0 <botname> [lines]"}
LINES=${2:-50}
SVC="telebots-${BOT}.service"
echo "=== $SVC (last $LINES lines, then following) ==="
journalctl -u "$SVC" -n "$LINES" -f

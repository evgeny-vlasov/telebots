#!/usr/bin/env bash
# scripts/add_bot.sh <botname> <port>
# Scaffold a new bot from the anglers template.
# Example: ./scripts/add_bot.sh fisherman 5011
set -euo pipefail

BOTNAME=${1:?"Usage: $0 <botname> <port>"}
PORT=${2:?"Usage: $0 <botname> <port>"}
TELEBOTS_DIR="/opt/telebots"
SRC="$TELEBOTS_DIR/bots/anglers"
DST="$TELEBOTS_DIR/bots/$BOTNAME"

if [ -d "$DST" ]; then
    echo "Error: $DST already exists."
    exit 1
fi

echo "Scaffolding bot: $BOTNAME on port $PORT"
cp -r "$SRC" "$DST"
mkdir -p "$DST/knowledge_base"
rm -f "$DST/knowledge_base"/*.txt   # clear anglers KB files

# Patch config.py
sed -i "s/BOT_ID = \"anglers\"/BOT_ID = \"$BOTNAME\"/" "$DST/config.py"
sed -i "s/BOT_NAME = \"Alberta Anglers Guide\"/BOT_NAME = \"$BOTNAME\"/" "$DST/config.py"
sed -i "s/PORT = 5010/PORT = $PORT/" "$DST/config.py"
sed -i "s/ANGLERS_BOT_TOKEN/${BOTNAME^^}_BOT_TOKEN/" "$DST/config.py"

# systemd service
SVC_DST="/etc/systemd/system/telebots-${BOTNAME}.service"
sudo cp "$TELEBOTS_DIR/deploy/bot-template.service" "$SVC_DST"
sudo sed -i "s/<BOT_DISPLAY_NAME>/$BOTNAME/g" "$SVC_DST"
sudo sed -i "s/<BOTNAME>/$BOTNAME/g" "$SVC_DST"
sudo systemctl daemon-reload
sudo systemctl enable "telebots-$BOTNAME"

echo ""
echo "✓ Bot scaffolded at $DST"
echo ""
echo "Next steps:"
echo "  1. Add ${BOTNAME^^}_BOT_TOKEN to /opt/telebots/.env"
echo "  2. Add /telebots/$BOTNAME/webhook location to nginx-telebots.conf"
echo "  3. Add knowledge base files to $DST/knowledge_base/"
echo "  4. Edit $DST/prompts.py and $DST/config.py"
echo "  5. python3 $DST/load_kb.py"
echo "  6. sudo systemctl start telebots-$BOTNAME"
echo "  7. Register webhook with Telegram"

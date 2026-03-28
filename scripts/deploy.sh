#!/usr/bin/env bash
# scripts/deploy.sh
# Initial deployment of telebots on bebia.
# Run once from /opt/telebots after cloning.
set -euo pipefail

TELEBOTS_DIR="/opt/telebots"
VENV="$TELEBOTS_DIR/venv"

echo "=== Telebots deploy ==="
echo "Dir: $TELEBOTS_DIR"

# 1. Virtualenv
if [ ! -d "$VENV" ]; then
    echo "Creating virtualenv..."
    python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"

# 2. Dependencies
echo "Installing requirements..."
pip install --upgrade pip -q
pip install -r "$TELEBOTS_DIR/requirements.txt" -q
echo "  ✓ requirements installed"

# 3. .env check
if [ ! -f "$TELEBOTS_DIR/.env" ]; then
    echo ""
    echo "  ⚠  No .env found! Copy and fill in:"
    echo "     cp $TELEBOTS_DIR/.env.example $TELEBOTS_DIR/.env"
    echo "     nano $TELEBOTS_DIR/.env"
    exit 1
fi
chmod 640 "$TELEBOTS_DIR/.env"
echo "  ✓ .env present"

# 4. DB schema
echo "Applying telebots schema additions..."
source "$TELEBOTS_DIR/.env"
psql "$DATABASE_URL" -f "$TELEBOTS_DIR/deploy/schema.sql"
echo "  ✓ schema applied"

# 5. Load anglers KB
echo "Loading anglers knowledge base..."
python3 "$TELEBOTS_DIR/bots/anglers/load_kb.py"

# 6. systemd service — anglers
SVC_SRC="$TELEBOTS_DIR/deploy/bot-template.service"
SVC_DST="/etc/systemd/system/telebots-anglers.service"
if [ ! -f "$SVC_DST" ]; then
    echo "Installing systemd service..."
    sudo cp "$SVC_SRC" "$SVC_DST"
    sudo sed -i 's/<BOT_DISPLAY_NAME>/Alberta Anglers Guide/g' "$SVC_DST"
    sudo sed -i 's/<BOTNAME>/anglers/g' "$SVC_DST"
    sudo systemctl daemon-reload
    sudo systemctl enable telebots-anglers
    echo "  ✓ service installed"
else
    echo "  (service already exists, skipping)"
fi

sudo systemctl restart telebots-anglers
sudo systemctl status telebots-anglers --no-pager | tail -5

echo ""
echo "=== Deploy complete ==="
echo "  Health: curl http://localhost:5010/health"
echo "  Logs:   ./scripts/logs.sh anglers"
echo ""
echo "  Don't forget to:"
echo "  1. Add nginx config: sudo cp deploy/nginx-telebots.conf /etc/nginx/sites-available/telebots"
echo "  2. Obtain SSL cert:  sudo certbot --nginx -d bots.yourdomain.com"
echo "  3. Register webhook: python3 -c \""
echo "       import sys; sys.path.insert(0,'.')"
echo "       from platform.telegram.helpers import set_webhook"
echo "       from bots.anglers.config import Config"
echo "       set_webhook(Config.BOT_TOKEN, Config.WEBHOOK_URL)\""

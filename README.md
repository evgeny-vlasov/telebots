# telebots

Telegram bot platform and bots. Runs on bebia alongside bot-army and webgarden.

**Stack:** Python · Flask · PostgreSQL + pgvector · Anthropic Claude · Voyage AI · Nginx · systemd  
**Server:** bebia (192.168.1.66) · Debian 12  
**Base path:** `/opt/telebots/`

---

## Structure

```
telebots/
├── platform/                   # Shared platform — used by all bots
│   ├── config.py               # Global config loader (.env)
│   ├── database.py             # DB connection helpers
│   ├── claude_client.py        # Anthropic API wrapper
│   ├── rag/                    # RAG subsystem
│   │   ├── embedder.py         # Chunk and embed documents
│   │   ├── retriever.py        # Vector search
│   │   └── voyage_client.py    # Voyage AI embeddings
│   └── telegram/
│       ├── webhook.py          # Webhook receiver (Flask blueprint)
│       └── helpers.py          # Telegram API helpers (send, reply, etc.)
│
├── bots/
│   └── anglers/                # Alberta Anglers Guide bot
│       ├── app.py              # Flask app — webhook + web blueprints
│       ├── config.py           # Bot config (port, bot_id, token)
│       ├── prompts.py          # System prompts
│       ├── rag_config.py       # RAG settings
│       ├── web.py              # Simple web face (status/info page)
│       ├── load_kb.py          # Knowledge base loader script
│       └── knowledge_base/     # .txt knowledge files
│
├── scripts/
│   ├── deploy.sh               # Initial deploy on bebia
│   ├── restart.sh              # Restart one or all bot services
│   ├── logs.sh                 # Tail logs for a bot
│   ├── status.sh               # Show status of all telebots services
│   └── add_bot.sh              # Scaffold a new bot
│
├── deploy/
│   ├── bot-template.service    # systemd unit template
│   └── nginx-telebots.conf     # Nginx snippet for all telebots
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── ADDING_A_BOT.md
│
├── .env.example
└── requirements.txt
```

---

## Port Allocation

| Bot      | Port | Service name              |
|----------|------|---------------------------|
| anglers  | 5010 | telebots-anglers.service  |
| (next)   | 5011 | telebots-xxx.service      |

Clear of bot-army (5001–5002) and webgarden (8001–8002, 5003).

---

## Quick Start (bebia)

```bash
# Clone
cd /opt
sudo git clone https://github.com/evgeny-vlasov/telebots.git
sudo chown -R chip:chip telebots
cd telebots

# Virtualenv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Config
cp .env.example .env
nano .env   # fill in tokens and keys

# DB (reuses botfarm db from bot-army — just run the telebots schema)
psql -U botfarm -d botfarm -f deploy/schema.sql

# Load knowledge base
python3 bots/anglers/load_kb.py

# Register Telegram webhook
python3 -c "
import sys; sys.path.insert(0,'.')
from platform.telegram.helpers import set_webhook
from bots.anglers.config import Config
set_webhook(Config.BOT_TOKEN, Config.WEBHOOK_URL)
"

# Deploy service
sudo cp deploy/bot-template.service /etc/systemd/system/telebots-anglers.service
sudo nano /etc/systemd/system/telebots-anglers.service   # fill placeholders
sudo systemctl daemon-reload
sudo systemctl enable --now telebots-anglers

# Verify
sudo systemctl status telebots-anglers
curl http://localhost:5010/health
```

---

## Adding a Bot

```bash
./scripts/add_bot.sh <botname> <port>
# Example: ./scripts/add_bot.sh fisherman 5011
```

See `docs/ADDING_A_BOT.md` for the full walkthrough.

---

## Related Projects

- **bot-army** → `/opt/bot-farm/` — web widget bots (keystone, therapist)
- **webgarden** → `/var/www/webgarden/` — Flask websites
- **Shared DB** → `botfarm` PostgreSQL + pgvector

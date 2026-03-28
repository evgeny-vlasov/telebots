# Adding a New Bot

The fast path is the scaffold script. The manual path is below for reference.

---

## Fast path

```bash
cd /opt/telebots
./scripts/add_bot.sh <botname> <port>
# e.g.: ./scripts/add_bot.sh fisherman 5011
```

Then follow the printed checklist.

---

## Manual path (step by step)

### 1. Pick a port

Check `docs/ARCHITECTURE.md` port table. Next available starts at 5011.

### 2. Create bot directory

```bash
cp -r /opt/telebots/bots/anglers /opt/telebots/bots/<botname>
mkdir -p /opt/telebots/bots/<botname>/knowledge_base
```

### 3. Edit config.py

```python
BOT_ID   = "<botname>"
BOT_NAME = "Your Bot Display Name"
PORT     = 5011
BOT_TOKEN: str = os.environ["<BOTNAME>_BOT_TOKEN"]
```

### 4. Add token to .env

```bash
echo '<BOTNAME>_BOT_TOKEN=your_token_here' >> /opt/telebots/.env
```

Get the token from @BotFather on Telegram.

### 5. Write prompts.py

Edit `bots/<botname>/prompts.py` — replace the system prompt with
your bot's persona and instructions.

### 6. Add knowledge base files

Drop `.txt` files into `bots/<botname>/knowledge_base/`.
Plain text, clear sections. See anglers KB as example.

### 7. Load knowledge base

```bash
cd /opt/telebots
source venv/bin/activate
python3 bots/<botname>/load_kb.py
```

### 8. Add nginx location blocks

In `/etc/nginx/sites-available/telebots`, add:

```nginx
upstream telebots_<botname> {
    server 127.0.0.1:<port>;
}

# inside the server block:
location /<botname>/ {
    proxy_pass http://telebots_<botname>/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /<botname>/webhook {
    proxy_pass         http://telebots_<botname>/webhook;
    proxy_read_timeout 30s;
    proxy_set_header   Host $host;
    proxy_set_header   X-Forwarded-Proto $scheme;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 9. Install and start systemd service

```bash
sudo cp /opt/telebots/deploy/bot-template.service \
        /etc/systemd/system/telebots-<botname>.service

# Edit: replace <BOTNAME> and <BOT_DISPLAY_NAME>
sudo nano /etc/systemd/system/telebots-<botname>.service

sudo systemctl daemon-reload
sudo systemctl enable --now telebots-<botname>
sudo systemctl status telebots-<botname>
```

### 10. Register webhook with Telegram

```bash
cd /opt/telebots
source venv/bin/activate
python3 - << 'PYEOF'
import sys; sys.path.insert(0, '.')
from platform.telegram.helpers import set_webhook, get_webhook_info
from bots.<botname>.config import Config
set_webhook(Config.BOT_TOKEN, Config.WEBHOOK_URL)
print(get_webhook_info(Config.BOT_TOKEN))
PYEOF
```

### 11. Verify

```bash
curl http://localhost:<port>/health
./scripts/logs.sh <botname>
```

Open Telegram, send a message to your bot. Check logs.

---

## Checklist

- [ ] Port allocated and documented in ARCHITECTURE.md
- [ ] `bots/<botname>/` directory created
- [ ] `config.py` updated (BOT_ID, BOT_NAME, PORT, token env var)
- [ ] Token added to `/opt/telebots/.env`
- [ ] `prompts.py` written
- [ ] Knowledge base files added
- [ ] `load_kb.py` run successfully
- [ ] Nginx location blocks added and nginx reloaded
- [ ] systemd service installed, enabled, started
- [ ] Webhook registered with Telegram
- [ ] Health check passes
- [ ] Test message in Telegram works
- [ ] Port table in ARCHITECTURE.md updated

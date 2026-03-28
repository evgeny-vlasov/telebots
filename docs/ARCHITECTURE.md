# Architecture

## Overview

```
Internet
   │
   └─ Nginx (SSL, routing)
         │
         ├─ /anglers/webhook  ──► Flask :5010  ──► handle_message()
         │                                              │
         │                                        RAG retrieval
         │                                        (pgvector / botfarm DB)
         │                                              │
         │                                        Claude API
         │                                              │
         │                                        Telegram reply
         │
         ├─ /anglers/          ──► Flask :5010/  (web face)
         └─ /nextbot/webhook   ──► Flask :5011   (future bot)
```

## Platform vs Bot

**`platform/`** is a shared library. It knows nothing about any specific bot.

| Module | Purpose |
|---|---|
| `platform/config.py` | Load `.env`, expose typed settings |
| `platform/database.py` | `get_connection()`, `get_cursor()` context manager |
| `platform/claude_client.py` | `chat(system, messages)` → string |
| `platform/rag/embedder.py` | Chunk text, embed, write to DB |
| `platform/rag/retriever.py` | Vector search → context string |
| `platform/rag/voyage_client.py` | Voyage AI embed API |
| `platform/telegram/webhook.py` | Flask blueprint factory |
| `platform/telegram/helpers.py` | `send_message`, `set_webhook`, etc. |

**`bots/<name>/`** is a self-contained bot. It imports from platform and adds:

| File | Purpose |
|---|---|
| `app.py` | Wires Flask app, registers blueprints, implements `handle_message()` |
| `config.py` | Port, BOT_TOKEN, WEBHOOK_URL |
| `prompts.py` | System prompt(s) |
| `rag_config.py` | TOP_K, threshold, chunk sizes |
| `web.py` | Minimal public web page |
| `load_kb.py` | Script to embed and store KB docs |
| `knowledge_base/*.txt` | Plain text knowledge files |

## Database

Telebots shares the `botfarm` PostgreSQL database with bot-army.
This avoids running two PG instances and keeps all bot data in one place.

Core tables (owned by bot-army schema):
- `bots` — one row per bot
- `documents` + `document_chunks` — RAG corpus with pgvector embeddings
- `conversations` + `messages` — chat history (optional, in-memory by default)
- `leads` — not used by telebots

Telebots additions (`deploy/schema.sql`):
- `telegram_sessions` — per-chat tracking
- `location_shares` — geolocation log

## Telegram Webhook Flow

```
Telegram server
  POST /anglers/webhook
    └─ Nginx proxies to 127.0.0.1:5010/webhook
         └─ webhook.py blueprint receives JSON update
              └─ extracts chat_id + text
              └─ calls handle_message(update, chat_id, text)
                   └─ retrieve() — pgvector similarity search
                   └─ build_system_prompt(context)
                   └─ claude_client.chat(system, history)
                   └─ returns reply string
              └─ send_message(token, chat_id, reply)
              └─ returns 200 OK to Telegram
```

Telegram expects a 200 response within ~5 seconds, or it will retry.
The Claude API call typically takes 1–3s, well within budget.

## Conversation Memory

Conversation history is kept in-memory per `chat_id` in a plain dict.
This is intentionally simple:
- No DB writes per message (fast)
- Cleared on service restart (acceptable)
- MAX_HISTORY = 10 pairs to keep context window manageable

If persistence is needed, write history to the `messages` table.

## Ports

| Service | Port | Notes |
|---|---|---|
| telebots-anglers | 5010 | |
| (next bot) | 5011 | |
| bot-army keystone | 5001 | don't touch |
| bot-army therapist | 5002 | don't touch |
| webgarden birds | 5003 | don't touch |
| webgarden psyling | 8001 | don't touch |
| webgarden keystone | 8002 | don't touch |

"""
bots/anglers/app.py
Alberta Anglers Guide — Flask application.
Mounts:
  /webhook   ← Telegram webhook receiver
  /          ← Simple web face (status / info)
"""
import sys
from pathlib import Path

# Make platform importable when running directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from flask import Flask
from .config import Config
from .prompts import build_system_prompt
from .rag_config import TOP_K_CHUNKS, SIMILARITY_THRESHOLD
from platform.claude_client import chat
from platform.rag.retriever import retrieve, format_context
from platform.telegram.webhook import make_webhook_blueprint
from platform.database import get_cursor
from .web import web_bp


def get_bot_db_id() -> int:
    with get_cursor() as cur:
        cur.execute("SELECT id FROM bots WHERE bot_id = %s", (Config.BOT_ID,))
        row = cur.fetchone()
        if not row:
            raise RuntimeError(f"Bot '{Config.BOT_ID}' not registered in DB. "
                               "Run: INSERT INTO bots (bot_id, bot_name) "
                               f"VALUES ('{Config.BOT_ID}', '{Config.BOT_NAME}');")
        return row["id"]


# In-memory conversation history per chat_id
# { chat_id: [{"role": "user"|"assistant", "content": "..."}] }
_conversations: dict[int, list] = {}
MAX_HISTORY = 10  # message pairs to keep


def handle_message(update: dict, chat_id: int, text: str) -> str:
    """Core message handler — RAG + Claude."""
    bot_db_id = get_bot_db_id()

    # Handle /start
    if text.startswith("/start"):
        _conversations[chat_id] = []
        return (
            "🎣 *Alberta Anglers Guide*\n\n"
            "Hi! I can help you with fishing regulations, stocking info, "
            "species advice, and what's biting right now in Alberta.\n\n"
            "Share your location or just ask — e.g. _'What can I catch near "
            "Calgary right now?'_ or _'Rules for walleye on Lac Ste. Anne?'_"
        )

    # Handle /reset
    if text.startswith("/reset"):
        _conversations[chat_id] = []
        return "Conversation reset. What are you fishing for?"

    # Handle location share
    msg = update.get("message", {})
    if "location" in msg:
        lat = msg["location"]["latitude"]
        lon = msg["location"]["longitude"]
        text = f"I'm at coordinates {lat}, {lon}. What can I fish here and what are the regulations?"

    # RAG retrieval
    chunks = retrieve(text, bot_db_id,
                      top_k=TOP_K_CHUNKS,
                      threshold=SIMILARITY_THRESHOLD)
    context = format_context(chunks)

    # Build conversation history
    history = _conversations.setdefault(chat_id, [])
    history.append({"role": "user", "content": text})

    # Trim to keep context window manageable
    if len(history) > MAX_HISTORY * 2:
        history = history[-(MAX_HISTORY * 2):]
        _conversations[chat_id] = history

    system = build_system_prompt(context)
    reply = chat(system_prompt=system, messages=history)

    history.append({"role": "assistant", "content": reply})
    return reply


def create_app() -> Flask:
    app = Flask(__name__)

    # Webhook blueprint mounted at /anglers (nginx strips the prefix)
    webhook_bp = make_webhook_blueprint(Config, handle_message)
    app.register_blueprint(webhook_bp)

    # Web face
    app.register_blueprint(web_bp)

    @app.get("/health")
    def health():
        return {"bot": Config.BOT_ID, "status": "healthy"}

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="127.0.0.1", port=Config.PORT, debug=Config.DEBUG)

"""
platform/telegram/webhook.py
Flask blueprint factory for receiving Telegram webhook updates.
Each bot instantiates this with its own token and handler.
"""
from flask import Blueprint, request, jsonify
from .helpers import send_message, send_chat_action


def make_webhook_blueprint(bot_config, message_handler) -> Blueprint:
    """
    Returns a Flask blueprint mounted at /webhook.

    bot_config   — the bot's Config class (needs BOT_TOKEN, BOT_ID)
    message_handler(update, chat_id, text) → str  — bot-specific logic
    """
    bp = Blueprint(f"webhook_{bot_config.BOT_ID}", __name__)

    @bp.post("/webhook")
    def webhook():
        update = request.get_json(silent=True)
        if not update:
            return jsonify(ok=True)

        # Handle text messages and location shares
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return jsonify(ok=True)

        chat_id = msg["chat"]["id"]

        # Check for location share first
        if "location" in msg:
            lat = msg["location"]["latitude"]
            lng = msg["location"]["longitude"]
            text = f"I'm at coordinates {lat}, {lng}. What can I fish here and what are the regulations?"
        else:
            # Regular text message
            text = msg.get("text", "").strip()
            if not text:
                return jsonify(ok=True)

        # Show typing indicator
        send_chat_action(bot_config.BOT_TOKEN, chat_id)

        try:
            reply = message_handler(update, chat_id, text)
        except Exception as exc:
            reply = "Sorry, something went wrong. Please try again."
            import traceback; traceback.print_exc()

        send_message(bot_config.BOT_TOKEN, chat_id, reply)
        return jsonify(ok=True)

    return bp

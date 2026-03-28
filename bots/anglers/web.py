"""
bots/anglers/web.py
Simple web face — a single public page that shows bot info and status.
Served at / on the bot's port (proxied by nginx).
Intentionally minimal: this is a Telegram bot, not a web app.
"""
from flask import Blueprint, render_template_string
from .config import Config

web_bp = Blueprint("web", __name__)

_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ name }}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0d1117; color: #c9d1d9;
      display: flex; align-items: center; justify-content: center;
      min-height: 100vh; padding: 2rem;
    }
    .card {
      max-width: 480px; width: 100%;
      background: #161b22; border: 1px solid #30363d;
      border-radius: 12px; padding: 2.5rem;
      text-align: center;
    }
    .emoji { font-size: 3rem; margin-bottom: 1rem; }
    h1 { font-size: 1.5rem; color: #e6edf3; margin-bottom: 0.5rem; }
    p  { color: #8b949e; line-height: 1.6; margin: 0.75rem 0; }
    .status {
      display: inline-block; margin-top: 1.25rem;
      background: #1f6feb22; border: 1px solid #1f6feb;
      color: #58a6ff; border-radius: 20px;
      padding: 0.3rem 1rem; font-size: 0.85rem;
    }
    a { color: #58a6ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="card">
    <div class="emoji">🎣</div>
    <h1>{{ name }}</h1>
    <p>A Telegram bot for Alberta anglers — regulations, stocking info,
       species advice, and what's biting right now.</p>
    <p>Find me on Telegram: <a href="https://t.me/{{ handle }}">@{{ handle }}</a></p>
    <span class="status">● online</span>
  </div>
</body>
</html>
"""


@web_bp.get("/")
def index():
    return render_template_string(
        _PAGE,
        name=Config.BOT_NAME,
        # Set ANGLERS_BOT_HANDLE in .env or hardcode once known
        handle="AlbertaAnglersBot",
    )

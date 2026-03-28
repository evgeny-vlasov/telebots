"""
bots/anglers/config.py
Alberta Anglers Guide bot configuration.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class Config:
    BOT_ID = "anglers"
    BOT_NAME = "Alberta Anglers Guide"
    PORT = 5010
    DEBUG = False

    BOT_TOKEN: str = os.environ["ANGLERS_BOT_TOKEN"]

    _base = os.getenv("WEBHOOK_BASE_URL", "").rstrip("/")
    WEBHOOK_URL: str = f"{_base}/anglers/webhook"

    KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"

"""
platform/config.py
Global config — loads .env from /opt/telebots/.env (or local .env for dev).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Walk up from here to find .env
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")


class PlatformConfig:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
    VOYAGE_API_KEY: str = os.environ["VOYAGE_API_KEY"]
    WEBHOOK_BASE_URL: str = os.getenv("WEBHOOK_BASE_URL", "")

#!/usr/bin/env python3
"""
bots/anglers/load_kb.py
Load / reload the Alberta Anglers Guide knowledge base into botfarm DB.

Usage:
    cd /opt/telebots
    source venv/bin/activate
    python3 bots/anglers/load_kb.py

Safe to re-run — clears existing chunks before loading.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from bots.anglers.config import Config
from bots.anglers.rag_config import CHUNK_SIZE, CHUNK_OVERLAP
from telebots_platform.database import get_cursor
from telebots_platform.rag.embedder import load_document, clear_bot_chunks


def get_or_create_bot_db_id() -> int:
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM bots WHERE bot_id = %s", (Config.BOT_ID,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute(
            "INSERT INTO bots (bot_id, bot_name, port) VALUES (%s, %s, %s) RETURNING id",
            (Config.BOT_ID, Config.BOT_NAME, Config.PORT),
        )
        return cur.fetchone()["id"]


def main():
    kb_dir = Config.KNOWLEDGE_BASE_DIR
    txt_files = sorted(kb_dir.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {kb_dir}")
        sys.exit(1)

    print(f"Bot: {Config.BOT_NAME} ({Config.BOT_ID})")
    bot_db_id = get_or_create_bot_db_id()
    print(f"DB id: {bot_db_id}")

    print("Clearing existing chunks...")
    clear_bot_chunks(bot_db_id)

    total = 0
    for i, path in enumerate(txt_files, 1):
        content = path.read_text(encoding="utf-8").strip()
        print(f"[{i}/{len(txt_files)}] {path.name} ({len(content)} chars) ... ", end="")
        n = load_document(
            bot_db_id=bot_db_id,
            title=path.stem.replace("_", " ").title(),
            content=content,
            source=path.name,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        )
        print(f"✓ {n} chunks")
        total += n

    print(f"\nTotal chunks: {total}")
    print("✓ Knowledge base loaded successfully!")


if __name__ == "__main__":
    main()

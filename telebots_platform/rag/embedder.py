"""
platform/rag/embedder.py
Chunk text and write embeddings to document_chunks.
Identical schema to bot-army so both projects share the botfarm DB.
"""
import textwrap
from ..database import get_cursor
from .voyage_client import embed


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into overlapping word chunks."""
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return [c for c in chunks if c.strip()]


def load_document(bot_db_id: int, title: str, content: str, source: str = "",
                  chunk_size: int = 300, overlap: int = 50) -> int:
    """Insert document + chunks into botfarm DB. Returns chunk count."""
    chunks = chunk_text(content, chunk_size, overlap)
    embeddings = embed(chunks, input_type="document")

    with get_cursor(commit=True) as cur:
        # Insert parent document
        cur.execute(
            """
            INSERT INTO documents (bot_id, title, content, source)
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (bot_db_id, title, content, source),
        )
        doc_id = cur.fetchone()["id"]

        # Insert chunks
        for idx, (chunk, vec) in enumerate(zip(chunks, embeddings)):
            cur.execute(
                """
                INSERT INTO document_chunks
                    (document_id, bot_id, chunk_text, chunk_index, embedding)
                VALUES (%s, %s, %s, %s, %s::vector)
                """,
                (doc_id, bot_db_id, chunk, idx, str(vec)),
            )

    return len(chunks)


def clear_bot_chunks(bot_db_id: int) -> None:
    """Remove all chunks and documents for a bot (before reload)."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM document_chunks WHERE bot_id = %s", (bot_db_id,))
        cur.execute("DELETE FROM documents WHERE bot_id = %s", (bot_db_id,))

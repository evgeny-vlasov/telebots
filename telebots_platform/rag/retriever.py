"""
platform/rag/retriever.py
Vector similarity search against document_chunks.
"""
from ..database import get_cursor
from .voyage_client import embed


def retrieve(query: str, bot_db_id: int, top_k: int = 5,
             threshold: float = 0.3) -> list[dict]:
    """
    Return top_k relevant chunks for a query.
    Each result: {chunk_text, similarity}
    """
    [query_vec] = embed([query], input_type="query")

    with get_cursor() as cur:
        cur.execute(
            """
            SELECT chunk_text,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM   document_chunks
            WHERE  bot_id = %s
              AND  1 - (embedding <=> %s::vector) >= %s
            ORDER  BY similarity DESC
            LIMIT  %s
            """,
            (str(query_vec), bot_db_id, str(query_vec), threshold, top_k),
        )
        return cur.fetchall()


def format_context(chunks: list[dict]) -> str:
    """Turn retrieved chunks into a context block for the system prompt."""
    if not chunks:
        return ""
    parts = [f"[{i+1}] {c['chunk_text']}" for i, c in enumerate(chunks)]
    return "RELEVANT KNOWLEDGE BASE CONTEXT:\n\n" + "\n\n".join(parts)

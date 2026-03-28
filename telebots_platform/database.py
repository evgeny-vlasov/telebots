"""
platform/database.py
PostgreSQL + pgvector connection helpers.
Reuses the botfarm database shared with bot-army.
"""
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from .config import PlatformConfig


def get_connection():
    return psycopg2.connect(
        PlatformConfig.DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


@contextmanager
def get_cursor(commit: bool = False):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
            if commit:
                conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

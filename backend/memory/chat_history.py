"""
backend/memory/chat_history.py
-------------------------------
SQLite-based chat history.
Stored on Google Drive so it persists between Colab sessions.
"""

import os
import sqlite3
from datetime import datetime

# ── DB path from env (Google Drive in Colab) ─────────────────────────────────
DB_PATH = os.environ.get("SQLITE_PATH", "./backend/data/chat_history.db")

# ── Initialize DB once ───────────────────────────────────────────────────────
def _init_db():
    """Create the messages table if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT    NOT NULL,
            role       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            timestamp  TEXT    NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)")
    conn.commit()
    conn.close()
    print(f"[ChatHistory] SQLite ready at: {DB_PATH}")

_init_db()


def save_message(session_id: str, role: str, content: str):
    """
    Save a single message to the DB.

    Args:
        session_id : Unique session identifier
        role       : "user" or "assistant"
        content    : Message text
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 10) -> list[dict]:
    """
    Get the last N messages for a session (for context window).

    Returns:
        List of {"role": "user"/"assistant", "content": "..."}
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT role, content FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit)
    ).fetchall()
    conn.close()

    # Reverse so oldest is first (correct order for LLM)
    return [{"role": r, "content": c} for r, c in reversed(rows)]


def get_full_history(session_id: str) -> list[dict]:
    """Get ALL messages for a session (for display in UI)."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id",
        (session_id,)
    ).fetchall()
    conn.close()
    return [{"role": r, "content": c, "timestamp": t} for r, c, t in rows]


def clear_session(session_id: str):
    """Delete all messages for a session."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

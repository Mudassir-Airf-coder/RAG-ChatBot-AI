import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


def _now() -> str:
    return datetime.now(UTC).isoformat()


def init_db(sqlite_path: str) -> None:
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PROCESSING',
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT 'New chat',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            citations TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
        CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats(updated_at DESC);
    """)
    conn.close()


def _connect(sqlite_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_document(
    document_id: str,
    filename: str,
    status: str = "PROCESSING",
    error_message: str | None = None,
    sqlite_path: str = ":memory:",
) -> dict:
    now = _now()
    conn = _connect(sqlite_path)
    conn.execute(
        "INSERT INTO documents (id, filename, status, error_message, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (document_id, filename, status, error_message, now, now),
    )
    conn.commit()
    conn.close()
    return {
        "id": document_id,
        "filename": filename,
        "status": status,
        "error_message": error_message,
        "created_at": now,
        "updated_at": now,
    }


def get_document(document_id: str, sqlite_path: str = ":memory:") -> dict | None:
    conn = _connect(sqlite_path)
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_documents(sqlite_path: str = ":memory:") -> list[dict]:
    conn = _connect(sqlite_path)
    rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_document_status(
    document_id: str,
    status: str,
    error_message: str | None = None,
    sqlite_path: str = ":memory:",
) -> None:
    conn = _connect(sqlite_path)
    conn.execute(
        "UPDATE documents SET status = ?, error_message = ?, updated_at = ? WHERE id = ?",
        (status, error_message, _now(), document_id),
    )
    conn.commit()
    conn.close()


def delete_document(document_id: str, sqlite_path: str = ":memory:") -> None:
    conn = _connect(sqlite_path)
    conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()


def mark_stale_processing_as_failed(sqlite_path: str, max_age_seconds: int = 300) -> int:
    cutoff = datetime.now(UTC).timestamp() - max_age_seconds
    conn = _connect(sqlite_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, created_at FROM documents WHERE status = 'PROCESSING'")
        stale_ids = []
        for doc_id, created in cur.fetchall():
            try:
                ts = datetime.fromisoformat(created).timestamp()
            except Exception:
                continue
            if ts < cutoff:
                stale_ids.append(doc_id)
        for doc_id in stale_ids:
            cur.execute(
                "UPDATE documents SET status = 'FAILED', "
                "error_message = 'Processing timed out', "
                "updated_at = ? WHERE id = ?",
                (_now(), doc_id),
            )
        conn.commit()
        return len(stale_ids)
    finally:
        conn.close()


def create_chat(
    chat_id: str,
    title: str = "New chat",
    sqlite_path: str = ":memory:",
) -> dict:
    now = _now()
    conn = _connect(sqlite_path)
    conn.execute(
        "INSERT INTO chats (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (chat_id, title, now, now),
    )
    conn.commit()
    conn.close()
    return {"id": chat_id, "title": title, "created_at": now, "updated_at": now}


def list_chats(sqlite_path: str = ":memory:") -> list[dict]:
    conn = _connect(sqlite_path)
    rows = conn.execute("SELECT * FROM chats ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_chat(chat_id: str, sqlite_path: str = ":memory:") -> dict | None:
    conn = _connect(sqlite_path)
    row = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_chat_timestamp(chat_id: str, sqlite_path: str = ":memory:") -> None:
    conn = _connect(sqlite_path)
    conn.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (_now(), chat_id))
    conn.commit()
    conn.close()


def delete_chat(chat_id: str, sqlite_path: str = ":memory:") -> None:
    conn = _connect(sqlite_path)
    conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()


def create_message(
    message_id: str,
    chat_id: str,
    role: str,
    content: str,
    citations: list[dict] | None = None,
    sqlite_path: str = ":memory:",
) -> dict:
    now = _now()
    citations_json = json.dumps(citations or [])
    conn = _connect(sqlite_path)
    conn.execute(
        "INSERT INTO messages (id, chat_id, role, content, citations, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (message_id, chat_id, role, content, citations_json, now),
    )
    conn.commit()
    conn.close()
    return {
        "id": message_id,
        "chat_id": chat_id,
        "role": role,
        "content": content,
        "citations": citations or [],
        "created_at": now,
    }


def get_messages_by_chat(chat_id: str, sqlite_path: str = ":memory:") -> list[dict]:
    conn = _connect(sqlite_path)
    rows = conn.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at", (chat_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["citations"] = json.loads(d["citations"])
        result.append(d)
    return result

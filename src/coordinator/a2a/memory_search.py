"""MemorySearch — 跨 Session 全文搜尋（SQLite FTS5）。"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/memory.db")


class MemorySearch:
    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_fts()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_fts(self) -> None:
        conn = self._conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                session_id TEXT DEFAULT ''
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS conversation_fts
                USING fts5(content, content_rowid='id', tokenize='unicode61');
        """)
        conn.close()

    def index_turn(self, user_id: int, role: str, content: str, session_id: str = "") -> None:
        conn = self._conn()
        ts = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "INSERT INTO conversation_history (user_id, role, content, timestamp, session_id) VALUES (?,?,?,?,?)",
            (user_id, role, content, ts, session_id),
        )
        conn.execute("INSERT INTO conversation_fts (rowid, content) VALUES (?,?)", (cursor.lastrowid, content))
        conn.commit()
        conn.close()

    def search(self, query: str, user_id: int | None = None, limit: int = 5) -> list[dict]:
        conn = self._conn()
        if user_id:
            rows = conn.execute(
                """SELECT h.role, h.content, h.timestamp FROM conversation_fts f
                   JOIN conversation_history h ON f.rowid = h.id
                   WHERE f.content MATCH ? AND h.user_id = ?
                   ORDER BY rank LIMIT ?""",
                (query, user_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT h.role, h.content, h.timestamp FROM conversation_fts f
                   JOIN conversation_history h ON f.rowid = h.id
                   WHERE f.content MATCH ?
                   ORDER BY rank LIMIT ?""",
                (query, limit),
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_context_for_query(self, query: str, user_id: int, max_chars: int = 1500) -> str:
        results = self.search(query, user_id, limit=5)
        if not results:
            return ""
        lines = ["[歷史回憶]"]
        total = 0
        for r in results:
            snippet = r["content"][:200]
            line = f"- ({r['role']}) {snippet}"
            if total + len(line) > max_chars:
                break
            lines.append(line)
            total += len(line)
        return "\n".join(lines)

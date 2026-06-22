"""事件日誌 — SQLite 記錄所有團隊事件。"""
from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path

log = logging.getLogger(__name__)


class EventLog:
    """SQLite 事件日誌，保留 30 天。"""

    def __init__(self, db_path: str = "state/events.db") -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                instance TEXT,
                event_type TEXT,
                detail TEXT
            )
        """)
        self._conn.commit()

    def log(self, instance: str, event_type: str, detail: str = "") -> None:
        self._conn.execute(
            "INSERT INTO events (timestamp, instance, event_type, detail) VALUES (?, ?, ?, ?)",
            (time.time(), instance, event_type, detail[:500]),
        )
        self._conn.commit()

    def query(self, instance: str | None = None, event_type: str | None = None,
              limit: int = 50) -> list[dict]:
        sql = "SELECT id, timestamp, instance, event_type, detail FROM events WHERE 1=1"
        params: list = []
        if instance:
            sql += " AND instance = ?"
            params.append(instance)
        if event_type:
            sql += " AND event_type = ?"
            params.append(event_type)
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return [{"id": r[0], "ts": r[1], "instance": r[2], "type": r[3], "detail": r[4]}
                for r in rows]

    def today_summary(self) -> dict:
        today_start = time.time() - (time.time() % 86400)
        rows = self._conn.execute(
            "SELECT event_type, COUNT(*) FROM events WHERE timestamp > ? GROUP BY event_type",
            (today_start,),
        ).fetchall()
        return {r[0]: r[1] for r in rows}

    def cleanup(self, days: int = 30) -> int:
        cutoff = time.time() - days * 86400
        cur = self._conn.execute("DELETE FROM events WHERE timestamp < ?", (cutoff,))
        self._conn.commit()
        return cur.rowcount

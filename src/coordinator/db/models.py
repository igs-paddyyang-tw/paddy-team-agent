"""資料庫模型 — 6 張表（aiosqlite async）。"""
from __future__ import annotations

import sqlite3
import aiosqlite
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("data/platform.db")


def get_db() -> sqlite3.Connection:
    """同步版（向後相容，供遷移期使用）。"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


async def get_async_db() -> aiosqlite.Connection:
    """取得 async DB 連線。"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(DB_PATH))
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    return conn


async def init_db() -> None:
    migrations_dir = Path(__file__).parent / "migrations"
    async with aiosqlite.connect(str(DB_PATH)) as conn:
        for sql_file in sorted(migrations_dir.glob("*.sql")):
            await conn.executescript(sql_file.read_text(encoding="utf-8"))
        await conn.commit()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Async Query helpers ──

async def insert(conn: aiosqlite.Connection, table: str, data: dict) -> str:
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    await conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", list(data.values()))
    await conn.commit()
    return data.get("id", "")


async def fetch_all(conn: aiosqlite.Connection, sql: str, params: tuple = ()) -> list[dict]:
    cursor = await conn.execute(sql, params)
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def fetch_one(conn: aiosqlite.Connection, sql: str, params: tuple = ()) -> dict | None:
    cursor = await conn.execute(sql, params)
    row = await cursor.fetchone()
    return dict(row) if row else None


# ── Task CRUD helpers ──

async def create_task(conn: aiosqlite.Connection, task_id: str, title: str,
                      assignee: str | None = None, description: str = "",
                      priority: int = 0, source: str = "manual") -> str:
    """建立任務。有 assignee 則自動進 QUEUED，否則 BACKLOG。"""
    status = "queued" if assignee else "backlog"
    ts = now_iso()
    await insert(conn, "tasks", {
        "id": task_id, "title": title, "description": description,
        "status": status, "assignee": assignee, "priority": priority,
        "source": source, "created_at": ts, "updated_at": ts,
    })
    await insert(conn, "task_events", {
        "task_id": task_id, "from_status": None, "to_status": status,
        "actor": "system", "message": f"Task created (source={source})",
        "created_at": ts,
    })
    return task_id


async def update_task_status(conn: aiosqlite.Connection, task_id: str,
                             to_status: str, actor: str, message: str = "") -> bool:
    """更新任務狀態 + 寫入 event。"""
    task = await fetch_one(conn, "SELECT status FROM tasks WHERE id=?", (task_id,))
    if not task:
        return False
    ts = now_iso()
    updates = f"status=?, updated_at=?"
    params: list[Any] = [to_status, ts]
    if to_status == "claimed":
        updates += ", claimed_at=?"
        params.append(ts)
    elif to_status in ("completed", "failed"):
        updates += ", completed_at=?"
        params.append(ts)
    elif to_status == "blocked":
        updates += ", blocked_reason=?"
        params.append(message)
    elif to_status == "queued":
        updates += ", blocked_reason=NULL, claimed_at=NULL"
    params.append(task_id)
    await conn.execute(f"UPDATE tasks SET {updates} WHERE id=?", params)
    await insert(conn, "task_events", {
        "task_id": task_id, "from_status": task["status"],
        "to_status": to_status, "actor": actor, "message": message,
        "created_at": ts,
    })
    await conn.commit()
    return True


async def get_board(conn: aiosqlite.Connection) -> dict[str, list[dict]]:
    """取得看板（按狀態分組）。"""
    rows = await fetch_all(conn, "SELECT * FROM tasks ORDER BY priority DESC, created_at")
    board: dict[str, list[dict]] = {
        "backlog": [], "queued": [], "claimed": [],
        "executing": [], "blocked": [], "completed": [], "failed": [],
    }
    for r in rows:
        s = r.get("status", "backlog")
        if s in board:
            board[s].append(r)
    return board

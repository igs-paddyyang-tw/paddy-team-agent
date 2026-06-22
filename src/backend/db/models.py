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
    migration = Path(__file__).parent / "migrations" / "001_init.sql"
    async with aiosqlite.connect(str(DB_PATH)) as conn:
        await conn.executescript(migration.read_text(encoding="utf-8"))
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

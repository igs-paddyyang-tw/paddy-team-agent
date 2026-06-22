"""MCP Tools 共用基礎設施。"""
from __future__ import annotations

_db = None


def get_db():
    """取得資料庫連線（延遲初始化）。"""
    global _db
    if _db is None:
        # 依專案需求初始化（SQLite / BigQuery / PostgreSQL）
        pass
    return _db


def init_tools(config: dict | None = None) -> None:
    """初始化工具依賴（由 daemon 啟動時呼叫）。"""
    pass

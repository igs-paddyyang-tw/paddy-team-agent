"""TaskLifecycle — 任務狀態機引擎。"""
from __future__ import annotations

import logging
from enum import StrEnum

from coordinator.db.models import (
    get_async_db, update_task_status, fetch_one, fetch_all, now_iso,
)
from coordinator.events.bus import EventBus
from coordinator.events.types import EventType, Event

log = logging.getLogger("task_lifecycle")


class TaskStatus(StrEnum):
    BACKLOG = "backlog"
    QUEUED = "queued"
    CLAIMED = "claimed"
    EXECUTING = "executing"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


# 合法狀態轉移表：(from, to)
VALID_TRANSITIONS: set[tuple[str, str]] = {
    ("backlog", "queued"),
    ("queued", "claimed"),
    ("claimed", "executing"),
    ("executing", "completed"),
    ("executing", "failed"),
    ("executing", "blocked"),
    ("blocked", "queued"),
    ("failed", "queued"),
}

CLAIM_TIMEOUT_SEC = 300


class TaskLifecycle:
    """任務狀態機引擎。"""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.event_bus = event_bus

    async def transition(self, task_id: str, to_status: str, actor: str, message: str = "") -> bool:
        """執行狀態轉移。驗證合法性 → 更新 DB → 發 EventBus。"""
        conn = await get_async_db()
        try:
            task = await fetch_one(conn, "SELECT * FROM tasks WHERE id=?", (task_id,))
            if not task:
                log.warning("Task %s not found", task_id)
                return False

            from_status = task["status"]
            if (from_status, to_status) not in VALID_TRANSITIONS:
                log.warning("Invalid transition: %s → %s (task=%s)", from_status, to_status, task_id)
                return False

            ok = await update_task_status(conn, task_id, to_status, actor, message)
            if ok and self.event_bus:
                await self.event_bus.emit(Event(
                    type=EventType.TASK_STATUS_CHANGED,
                    data={
                        "task_id": task_id,
                        "from": from_status,
                        "to": to_status,
                        "actor": actor,
                        "message": message,
                    },
                ))
            return ok
        finally:
            await conn.close()

    async def check_claim_timeout(self) -> list[dict]:
        """回傳 CLAIMED 超過 CLAIM_TIMEOUT_SEC 的任務。"""
        conn = await get_async_db()
        try:
            rows = await fetch_all(
                conn,
                "SELECT * FROM tasks WHERE status='claimed' AND claimed_at IS NOT NULL",
            )
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            stale: list[dict] = []
            for r in rows:
                claimed = datetime.fromisoformat(r["claimed_at"])
                if (now - claimed).total_seconds() > CLAIM_TIMEOUT_SEC:
                    stale.append(r)
            return stale
        finally:
            await conn.close()

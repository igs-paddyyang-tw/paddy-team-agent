"""Autopilot + Claim Monitor — 排程建任務 + 掛起偵測。"""
from __future__ import annotations

import asyncio
import logging
import uuid

from coordinator.db.models import get_async_db, create_task
from coordinator.task_lifecycle import TaskLifecycle

log = logging.getLogger("autopilot")

CLAIM_CHECK_INTERVAL = 60  # 每 60 秒檢查一次


async def claim_timeout_checker(
    lifecycle: TaskLifecycle,
    notify_fn=None,
) -> None:
    """背景任務：CLAIMED 超時偵測 + Telegram 告警。"""
    while True:
        try:
            stale = await lifecycle.check_claim_timeout()
            for task in stale:
                msg = f"⚠️ 任務 {task['id']} ({task['title'][:30]}) 已 CLAIMED 超過 5 分鐘，Agent 可能掛起"
                log.warning(msg)
                if notify_fn:
                    await notify_fn(msg)
        except Exception as e:
            log.error("claim_timeout_checker error: %s", e)
        await asyncio.sleep(CLAIM_CHECK_INTERVAL)


async def run_autopilot(config: dict) -> str | None:
    """執行單一 autopilot：建立任務並排入佇列。"""
    task_cfg = config.get("task", {})
    title = task_cfg.get("title", "Autopilot task")
    assignee = task_cfg.get("assignee")
    description = task_cfg.get("description", "")
    priority = task_cfg.get("priority", 0)

    task_id = f"ap-{uuid.uuid4().hex[:8]}"
    conn = await get_async_db()
    try:
        await create_task(
            conn, task_id, title,
            assignee=assignee, description=description,
            priority=priority, source="autopilot",
        )
        log.info("Autopilot created task %s: %s → %s", task_id, title, assignee)
        return task_id
    except Exception as e:
        log.error("Autopilot failed: %s", e)
        return None
    finally:
        await conn.close()

"""Audit Logger — 所有操作自動記錄。"""
from __future__ import annotations

import logging
import uuid

from coordinator.db.models import get_async_db, insert, now_iso
from coordinator.events.types import Event, EventType

log = logging.getLogger("audit_logger")

# 事件 → 審計動作映射
ACTION_MAP = {
    EventType.AGENT_STARTED: "agent.started",
    EventType.AGENT_STOPPED: "agent.stopped",
    EventType.TASK_CREATED: "issue.created",
    EventType.TASK_ASSIGNED: "issue.assigned",
    EventType.TASK_COMPLETED: "issue.completed",
    EventType.TASK_FAILED: "issue.failed",
    EventType.COST_RECORDED: "cost.recorded",
    EventType.BUDGET_WARNING: "budget.warning",
    EventType.SYSTEM_RESTART: "system.restart",
}


async def on_any_event(event: Event) -> None:
    """EventBus handler：記錄所有事件到 audit_events 表。"""
    action = ACTION_MAP.get(event.type)
    if not action:
        return

    data = event.data
    conn = await get_async_db()
    try:
        record = {
            "id": str(uuid.uuid4())[:8],
            "actor_type": data.get("actor_type", "system"),
            "actor_id": data.get("actor_id", data.get("agent_id", "")),
            "actor_name": data.get("actor_name", data.get("agent_id", "")),
            "action": action,
            "resource_type": _infer_resource_type(event.type),
            "resource_id": data.get("issue_id", data.get("agent_id", "")),
            "resource_name": data.get("title", ""),
            "details": str(data),
            "timestamp": event.timestamp,
        }
        await insert(conn, "audit_events", record)
        log.debug("Audit: %s by %s", action, record["actor_name"])
    finally:
        await conn.close()


def _infer_resource_type(event_type: EventType) -> str:
    if "AGENT" in event_type.value.upper():
        return "agent"
    if "TASK" in event_type.value.upper():
        return "issue"
    if "COST" in event_type.value.upper() or "BUDGET" in event_type.value.upper():
        return "cost"
    return "system"

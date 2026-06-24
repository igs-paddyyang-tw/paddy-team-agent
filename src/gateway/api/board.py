"""Board API — 任務看板（Kanban 風格）。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from coordinator.db.models import get_async_db, get_board, create_task, now_iso
from coordinator.task_lifecycle import TaskLifecycle

router = APIRouter()
_lifecycle = TaskLifecycle()


class CreateTaskBody(BaseModel):
    title: str
    description: str = ""
    assignee: str | None = None
    priority: int = 0
    source: str = "manual"


class TransitionBody(BaseModel):
    actor: str = "user"
    message: str = ""


@router.get("/board")
async def api_board():
    """看板 — 按狀態分組。"""
    conn = await get_async_db()
    try:
        return await get_board(conn)
    finally:
        await conn.close()


@router.post("/tasks")
async def api_create_task(body: CreateTaskBody):
    """建立任務。"""
    import uuid
    conn = await get_async_db()
    try:
        task_id = f"t-{uuid.uuid4().hex[:8]}"
        await create_task(
            conn, task_id, body.title,
            assignee=body.assignee, description=body.description,
            priority=body.priority, source=body.source,
        )
        return {"id": task_id, "status": "queued" if body.assignee else "backlog"}
    finally:
        await conn.close()


@router.patch("/tasks/{task_id}/unblock")
async def api_unblock(task_id: str, body: TransitionBody):
    """解除 BLOCKED → QUEUED。"""
    ok = await _lifecycle.transition(task_id, "queued", body.actor, body.message or "unblocked")
    if not ok:
        raise HTTPException(400, "無法 unblock（狀態不是 blocked 或任務不存在）")
    return {"task_id": task_id, "status": "queued"}


@router.patch("/tasks/{task_id}/retry")
async def api_retry(task_id: str, body: TransitionBody):
    """FAILED → QUEUED 重試。"""
    ok = await _lifecycle.transition(task_id, "queued", body.actor, body.message or "retry")
    if not ok:
        raise HTTPException(400, "無法 retry（狀態不是 failed 或任務不存在）")
    return {"task_id": task_id, "status": "queued"}


# ── Runtime API（Phase 2）──

_registry = None

def set_registry(registry):
    global _registry
    _registry = registry

@router.get("/runtimes")
async def api_runtimes():
    """列出所有 Runtime 狀態。"""
    if _registry:
        return _registry.get_all_status()
    return []

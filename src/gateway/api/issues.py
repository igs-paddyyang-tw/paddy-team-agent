from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from coordinator.db.models import get_async_db, insert, fetch_all, fetch_one, now_iso
from coordinator.events.types import EventType, Event

router = APIRouter()

class IssueCreate(BaseModel):
    title: str
    description: str = ""
    priority: int = 3
    assignee: str | None = None

class IssueAssign(BaseModel):
    assignee: str

class IssueStatusUpdate(BaseModel):
    status: str  # completed | failed
    output: str = ""

@router.get("")
async def list_issues(status: str | None = None):
    conn = await get_async_db()
    try:
        if status:
            return await fetch_all(conn, "SELECT * FROM issues WHERE status=? ORDER BY priority, created_at", (status,))
        return await fetch_all(conn, "SELECT * FROM issues ORDER BY priority, created_at")
    finally:
        await conn.close()

@router.post("", status_code=201)
async def create_issue(body: IssueCreate, request: Request):
    conn = await get_async_db()
    try:
        issue_id = str(uuid.uuid4())[:8]
        now = now_iso()
        data = {"id": issue_id, "title": body.title, "description": body.description,
                "status": "pending", "priority": body.priority, "assignee": body.assignee,
                "created_at": now, "updated_at": now}
        await insert(conn, "issues", data)
        bus = request.app.state.bus
        await bus.emit(Event(type=EventType.TASK_CREATED, data=data, source="api"))
        if body.assignee:
            await bus.emit(Event(type=EventType.TASK_ASSIGNED, data={"issue_id": issue_id, "assignee": body.assignee}, source="api"))
        return data
    finally:
        await conn.close()

@router.get("/{issue_id}")
async def get_issue(issue_id: str):
    conn = await get_async_db()
    try:
        issue = await fetch_one(conn, "SELECT * FROM issues WHERE id=?", (issue_id,))
        if not issue:
            raise HTTPException(404, "Issue not found")
        return issue
    finally:
        await conn.close()

@router.patch("/{issue_id}/assign")
async def assign_issue(issue_id: str, body: IssueAssign, request: Request):
    conn = await get_async_db()
    try:
        now = now_iso()
        await conn.execute("UPDATE issues SET assignee=?, status='assigned', updated_at=? WHERE id=?",
                     (body.assignee, now, issue_id))
        await conn.commit()
        bus = request.app.state.bus
        await bus.emit(Event(type=EventType.TASK_ASSIGNED, data={"issue_id": issue_id, "assignee": body.assignee}, source="api"))
        return await fetch_one(conn, "SELECT * FROM issues WHERE id=?", (issue_id,))
    finally:
        await conn.close()

@router.patch("/{issue_id}/complete")
async def complete_issue(issue_id: str, body: IssueStatusUpdate, request: Request):
    conn = await get_async_db()
    try:
        now = now_iso()
        status = body.status if body.status in ("completed", "failed") else "completed"
        await conn.execute("UPDATE issues SET status=?, completed_at=?, updated_at=? WHERE id=?",
                     (status, now, now, issue_id))
        await conn.commit()
        bus = request.app.state.bus
        event_type = EventType.TASK_COMPLETED if status == "completed" else EventType.TASK_FAILED
        await bus.emit(Event(type=event_type, data={"issue_id": issue_id, "output": body.output}, source="api"))
        return await fetch_one(conn, "SELECT * FROM issues WHERE id=?", (issue_id,))
    finally:
        await conn.close()

@router.delete("/{issue_id}", status_code=204)
async def delete_issue(issue_id: str):
    conn = await get_async_db()
    try:
        await conn.execute("DELETE FROM issues WHERE id=?", (issue_id,))
        await conn.commit()
    finally:
        await conn.close()

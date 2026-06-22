from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from coordinator.db.models import get_async_db, insert, fetch_all, fetch_one, now_iso
from coordinator.events.types import EventType, Event

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    role: str = "worker"
    provider: str = "kiro-cli"
    working_dir: str = "."
    model: str = "auto"

class AgentUpdate(BaseModel):
    status: str | None = None
    model: str | None = None

@router.get("/sessions")
async def agent_sessions_list():
    conn = await get_async_db()
    try:
        return await fetch_all(conn, "SELECT * FROM agent_sessions ORDER BY started_at DESC LIMIT 50")
    finally:
        await conn.close()


@router.get("")
async def list_agents():
    conn = await get_async_db()
    try:
        return await fetch_all(conn, "SELECT * FROM agents ORDER BY created_at")
    finally:
        await conn.close()

@router.post("", status_code=201)
async def create_agent(body: AgentCreate, request: Request):
    conn = await get_async_db()
    try:
        agent_id = str(uuid.uuid4())[:8]
        now = now_iso()
        data = {"id": agent_id, "name": body.name, "role": body.role, "provider": body.provider,
                "working_dir": body.working_dir, "model": body.model, "status": "idle",
                "created_at": now, "updated_at": now}
        await insert(conn, "agents", data)
        bus = request.app.state.bus
        await bus.emit(Event(type=EventType.AGENT_STARTED, data=data, source="api"))
        return data
    finally:
        await conn.close()

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    conn = await get_async_db()
    try:
        agent = await fetch_one(conn, "SELECT * FROM agents WHERE id=?", (agent_id,))
        if not agent:
            raise HTTPException(404, "Agent not found")
        return agent
    finally:
        await conn.close()

@router.patch("/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate):
    conn = await get_async_db()
    try:
        updates = {k: v for k, v in body.model_dump().items() if v is not None}
        if not updates:
            raise HTTPException(400, "No fields to update")
        updates["updated_at"] = now_iso()
        set_clause = ", ".join(f"{k}=?" for k in updates)
        await conn.execute(f"UPDATE agents SET {set_clause} WHERE id=?", [*updates.values(), agent_id])
        await conn.commit()
        return await fetch_one(conn, "SELECT * FROM agents WHERE id=?", (agent_id,))
    finally:
        await conn.close()

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, request: Request):
    conn = await get_async_db()
    try:
        await conn.execute("DELETE FROM agents WHERE id=?", (agent_id,))
        await conn.commit()
        bus = request.app.state.bus
        await bus.emit(Event(type=EventType.AGENT_STOPPED, data={"agent_id": agent_id}, source="api"))
    finally:
        await conn.close()


@router.post("/spawn")
async def spawn_agent(body: dict, request: Request):
    """動態啟動一個 agent（觸發 daemon）。"""
    name = body.get("name", "")
    bus = request.app.state.bus
    from coordinator.events.types import Event, EventType
    await bus.emit(Event(type=EventType.AGENT_STARTED, data={"agent_id": name, "action": "spawn"}, source="api"))
    return {"status": "spawning", "agent": name}

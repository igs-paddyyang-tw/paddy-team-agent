"""Admin API — Dashboard / Sessions / Costs / Audit / Queue。"""
from __future__ import annotations

from fastapi import APIRouter, Query, Request
from coordinator.db.models import get_async_db, fetch_all, fetch_one, now_iso

router = APIRouter()


# ── Dashboard ──────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def dashboard_stats():
    conn = await get_async_db()
    try:
        agents = await fetch_all(conn, "SELECT * FROM agents")
        active = sum(1 for a in agents if a["status"] != "offline")
        running = len(await fetch_all(conn, "SELECT id FROM issues WHERE status='assigned'"))
        today = now_iso()[:10]
        completed_today = len(await fetch_all(conn,
            "SELECT id FROM issues WHERE status='completed' AND completed_at LIKE ?", (f"{today}%",)))
        sessions_today = await fetch_all(conn,
            "SELECT cost_usd FROM agent_sessions WHERE started_at LIKE ?", (f"{today}%",))
        total_cost = sum(s["cost_usd"] or 0 for s in sessions_today)
        return {
            "active_agents": active,
            "running_tasks": running,
            "completed_today": completed_today,
            "total_cost_today_usd": round(total_cost, 4),
        }
    finally:
        await conn.close()


@router.get("/dashboard/trends")
async def dashboard_trends(days: int = 7):
    conn = await get_async_db()
    try:
        rows = await fetch_all(conn,
            "SELECT DATE(completed_at) as date, COUNT(*) as cnt FROM issues "
            "WHERE status='completed' AND completed_at IS NOT NULL "
            "GROUP BY DATE(completed_at) ORDER BY date DESC LIMIT ?", (days,))
        cost_rows = await fetch_all(conn,
            "SELECT DATE(recorded_at) as date, SUM(cost_usd) as total FROM cost_records "
            "GROUP BY DATE(recorded_at) ORDER BY date DESC LIMIT ?", (days,))
        return {
            "completed": {r["date"]: r["cnt"] for r in rows},
            "costs": {r["date"]: round(r["total"], 4) for r in cost_rows},
        }
    finally:
        await conn.close()


# ── Sessions ───────────────────────────────────────────────────

@router.get("/sessions")
async def list_sessions(agent_id: str | None = None, limit: int = 50):
    conn = await get_async_db()
    try:
        if agent_id:
            return await fetch_all(conn,
                "SELECT * FROM agent_sessions WHERE agent_id=? ORDER BY started_at DESC LIMIT ?",
                (agent_id, limit))
        return await fetch_all(conn, "SELECT * FROM agent_sessions ORDER BY started_at DESC LIMIT ?", (limit,))
    finally:
        await conn.close()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    conn = await get_async_db()
    try:
        return await fetch_one(conn, "SELECT * FROM agent_sessions WHERE id=?", (session_id,))
    finally:
        await conn.close()


# ── Costs ──────────────────────────────────────────────────────

@router.get("/costs")
async def get_costs(range: str = "7d", group_by: str = "agent"):
    conn = await get_async_db()
    try:
        rows = await fetch_all(conn, "SELECT * FROM cost_records ORDER BY recorded_at DESC LIMIT 500")
        total = sum(r["cost_usd"] for r in rows)

        by_agent: dict[str, float] = {}
        by_model: dict[str, float] = {}
        for r in rows:
            by_agent[r["agent_id"]] = by_agent.get(r["agent_id"], 0) + r["cost_usd"]
            by_model[r["model"]] = by_model.get(r["model"], 0) + r["cost_usd"]

        return {
            "total_usd": round(total, 4),
            "total_records": len(rows),
            "by_agent": {k: round(v, 4) for k, v in sorted(by_agent.items(), key=lambda x: -x[1])},
            "by_model": {k: round(v, 4) for k, v in sorted(by_model.items(), key=lambda x: -x[1])},
        }
    finally:
        await conn.close()


@router.get("/costs/budget")
async def get_budget():
    conn = await get_async_db()
    try:
        return await fetch_one(conn, "SELECT * FROM budget_configs WHERE workspace_id='default'")
    finally:
        await conn.close()


# ── Audit ──────────────────────────────────────────────────────

@router.get("/audit")
async def list_audit(
    actor: str | None = None,
    action: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    conn = await get_async_db()
    try:
        sql = "SELECT * FROM audit_events WHERE 1=1"
        params: list = []
        if actor:
            sql += " AND (actor_id=? OR actor_name LIKE ?)"
            params.extend([actor, f"%{actor}%"])
        if action:
            sql += " AND action LIKE ?"
            params.append(f"%{action}%")
        sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        events = await fetch_all(conn, sql, tuple(params))
        total = await fetch_one(conn, "SELECT COUNT(*) as cnt FROM audit_events")
        return {"total": total["cnt"] if total else 0, "events": events}
    finally:
        await conn.close()


# ── Queue ──────────────────────────────────────────────────────

@router.get("/queue")
async def list_queue():
    conn = await get_async_db()
    try:
        return await fetch_all(conn,
            "SELECT * FROM issues WHERE status IN ('pending','assigned') ORDER BY priority, created_at")
    finally:
        await conn.close()


@router.patch("/queue/{issue_id}/priority")
async def set_priority(issue_id: str, priority: int = Query(ge=1, le=4)):
    conn = await get_async_db()
    try:
        await conn.execute("UPDATE issues SET priority=?, updated_at=? WHERE id=?",
                     (priority, now_iso(), issue_id))
        await conn.commit()
        return await fetch_one(conn, "SELECT * FROM issues WHERE id=?", (issue_id,))
    finally:
        await conn.close()


@router.post("/queue/batch")
async def batch_action(body: dict):
    conn = await get_async_db()
    try:
        action = body.get("action")
        issue_ids = body.get("issue_ids", [])
        params = body.get("params", {})
        affected = 0
        now = now_iso()

        for iid in issue_ids:
            if action == "assign":
                await conn.execute("UPDATE issues SET assignee=?, status='assigned', updated_at=? WHERE id=?",
                             (params.get("agent"), now, iid))
                affected += 1
            elif action == "cancel":
                await conn.execute("UPDATE issues SET status='cancelled', updated_at=? WHERE id=?", (now, iid))
                affected += 1
            elif action == "set_priority":
                await conn.execute("UPDATE issues SET priority=?, updated_at=? WHERE id=?",
                             (params.get("priority", 3), now, iid))
                affected += 1
        await conn.commit()
        return {"action": action, "affected": affected}
    finally:
        await conn.close()


# ── Budget POST ───────────────────────────────────────────────

@router.post("/costs/budget")
async def set_budget(body: dict):
    conn = await get_async_db()
    try:
        daily = body.get("daily_limit_usd", 30.0)
        weekly = body.get("weekly_limit_usd", 150.0)
        threshold = body.get("alert_threshold", 80)
        await conn.execute(
            "UPDATE budget_configs SET daily_limit_usd=?, weekly_limit_usd=?, alert_threshold=? WHERE workspace_id='default'",
            (daily, weekly, threshold))
        await conn.commit()
        return await fetch_one(conn, "SELECT * FROM budget_configs WHERE workspace_id='default'")
    finally:
        await conn.close()


# ── Costs Export ──────────────────────────────────────────────

@router.get("/costs/export")
async def export_costs(format: str = "csv"):
    import csv, io
    conn = await get_async_db()
    try:
        rows = await fetch_all(conn, "SELECT * FROM cost_records ORDER BY recorded_at DESC")
        if format == "csv":
            buf = io.StringIO()
            if rows:
                writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(buf.getvalue(), media_type="text/csv",
                                     headers={"Content-Disposition": "attachment; filename=costs.csv"})
        return rows
    finally:
        await conn.close()


# ── Session Intervene ─────────────────────────────────────────

@router.post("/sessions/{session_id}/intervene")
async def intervene_session(session_id: str, body: dict, request: Request):
    action = body.get("action", "abort")
    message = body.get("message", "")
    bus = request.app.state.bus
    from coordinator.events.types import Event, EventType
    await bus.emit(Event(
        type=EventType.SYSTEM_RESTART if action == "retry" else EventType.AGENT_STOPPED,
        data={"session_id": session_id, "action": action, "message": message},
        source="admin_intervene",
    ))
    return {"status": "ok", "action": action, "session_id": session_id}


# ── Dashboard Live (redirect to WS) ──────────────────────────

@router.get("/dashboard/live")
def dashboard_live_info():
    return {"websocket_url": "/api/ws/events", "note": "Use WebSocket connection at /api/ws/events for live updates"}


# ── Route Aliases（對齊 Spec 路徑） ──────────────────────────

@router.get("/sessions/{agent_id}")
async def sessions_by_agent(agent_id: str, limit: int = 50):
    conn = await get_async_db()
    try:
        return await fetch_all(conn, "SELECT * FROM agent_sessions WHERE agent_id=? ORDER BY started_at DESC LIMIT ?", (agent_id, limit))
    finally:
        await conn.close()

@router.get("/sessions/{agent_id}/{session_id}")
async def session_detail(agent_id: str, session_id: str):
    conn = await get_async_db()
    try:
        return await fetch_one(conn, "SELECT * FROM agent_sessions WHERE id=? AND agent_id=?", (session_id, agent_id))
    finally:
        await conn.close()

@router.get("/system/health")
async def system_health():
    conn = await get_async_db()
    try:
        agents = await fetch_all(conn, "SELECT id, name, status FROM agents")
        return {"status": "ok", "agents": len(agents), "db": "connected"}
    finally:
        await conn.close()

@router.get("/dashboard/timeline")
async def dashboard_timeline(limit: int = 20):
    conn = await get_async_db()
    try:
        return await fetch_all(conn, "SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT ?", (limit,))
    finally:
        await conn.close()


@router.get("/costs/summary")
async def costs_summary():
    conn = await get_async_db()
    try:
        rows = await fetch_all(conn, "SELECT * FROM cost_records ORDER BY recorded_at DESC LIMIT 100")
        total = sum(r["cost_usd"] for r in rows)
        return {"total_usd": round(total, 4), "records": len(rows)}
    finally:
        await conn.close()


@router.post("/sessions/{agent_id}/{session_id}/intervene")
async def intervene_session_nested(agent_id: str, session_id: str, body: dict, request: Request):
    return await intervene_session(session_id, body, request)

"""Costs API — 費用追蹤（today/weekly/per-agent）。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
from coordinator.db.models import get_async_db, fetch_all, fetch_one

router = APIRouter()


@router.get("/today")
async def costs_today():
    """今日費用摘要。"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = await get_async_db()
    try:
        rows = await fetch_all(conn,
            "SELECT agent_id, SUM(cost_usd) as cost, SUM(total_tokens) as tokens, COUNT(*) as calls "
            "FROM agent_sessions WHERE started_at LIKE ? GROUP BY agent_id",
            (f"{today}%",))
        total = sum(r["cost"] or 0 for r in rows)
        budget = await fetch_one(conn, "SELECT daily_limit_usd FROM budget_configs WHERE workspace_id='default'")
        limit = budget["daily_limit_usd"] if budget else 30.0
        return {
            "date": today,
            "total_usd": round(total, 4),
            "budget_usd": limit,
            "usage_pct": round(total / limit * 100, 1) if limit else 0,
            "by_agent": [{
                "agent": r["agent_id"],
                "cost_usd": round(r["cost"] or 0, 4),
                "tokens": r["tokens"] or 0,
                "calls": r["calls"],
            } for r in sorted(rows, key=lambda x: -(x["cost"] or 0))],
        }
    finally:
        await conn.close()


@router.get("/weekly")
async def costs_weekly():
    """本週費用趨勢（過去 7 天）。"""
    conn = await get_async_db()
    try:
        rows = await fetch_all(conn,
            "SELECT DATE(started_at) as date, SUM(cost_usd) as cost, SUM(total_tokens) as tokens "
            "FROM agent_sessions WHERE started_at >= date('now', '-7 days') "
            "GROUP BY DATE(started_at) ORDER BY date")
        total = sum(r["cost"] or 0 for r in rows)
        return {
            "total_usd": round(total, 4),
            "days": [{
                "date": r["date"],
                "cost_usd": round(r["cost"] or 0, 4),
                "tokens": r["tokens"] or 0,
            } for r in rows],
        }
    finally:
        await conn.close()

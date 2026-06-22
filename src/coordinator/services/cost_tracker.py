"""Cost Tracker — 自動記錄每次 Agent spawn 的費用。"""
from __future__ import annotations

import logging
import uuid

from coordinator.db.models import get_async_db, insert, fetch_all, fetch_one, now_iso
from coordinator.events.types import Event, EventType

log = logging.getLogger("cost_tracker")

# 費率表（USD per 1K tokens）
COST_PER_1K = {
    "claude-4-opus": {"input": 0.015, "output": 0.075},
    "claude-4-sonnet": {"input": 0.003, "output": 0.015},
    "auto": {"input": 0.003, "output": 0.015},  # 預設用 sonnet 費率估算
}


def estimate_tokens(text: str) -> tuple[int, int]:
    """粗估 tokens（chars / 4）。"""
    chars = len(text)
    input_tokens = chars // 4
    output_tokens = chars * 3 // 4
    return input_tokens, output_tokens


async def on_agent_output(event: Event) -> None:
    """EventBus handler：agent.output → 記錄費用。"""
    data = event.data
    agent_id = data.get("agent_id", "")
    output = data.get("output", "")
    model = data.get("model", "auto")
    session_id = data.get("session_id", "")
    issue_id = data.get("issue_id", "")

    # 優先使用 event 中的實際 token 數
    input_tokens = data.get("input_tokens", 0)
    output_tokens = data.get("output_tokens", 0)
    if not (input_tokens and output_tokens):
        input_tokens, output_tokens = estimate_tokens(output)

    rates = COST_PER_1K.get(model, COST_PER_1K["auto"])
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1000

    conn = await get_async_db()
    try:
        record = {
            "id": str(uuid.uuid4())[:8],
            "agent_id": agent_id,
            "session_id": session_id,
            "issue_id": issue_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "recorded_at": now_iso(),
        }
        await insert(conn, "cost_records", record)
        log.debug("Cost recorded: %s $%.4f", agent_id, cost)

        # 檢查是否超預算
        await _check_budget(conn)
    except Exception as e:
        log.debug("Cost insert skipped: %s", e)
    finally:
        await conn.close()


async def _check_budget(conn) -> None:
    """檢查今日費用是否超過預算閾值。"""
    budget = await fetch_one(conn, "SELECT * FROM budget_configs WHERE workspace_id='default'")
    if not budget:
        return
    today = now_iso()[:10]
    rows = await fetch_all(conn, "SELECT cost_usd FROM cost_records WHERE recorded_at LIKE ?", (f"{today}%",))
    today_total = sum(r["cost_usd"] for r in rows)
    threshold = budget["daily_limit_usd"] * budget["alert_threshold"] / 100

    if today_total >= threshold:
        log.warning("⚠️ Budget warning: $%.2f / $%.2f (%.0f%%)",
                    today_total, budget["daily_limit_usd"],
                    today_total / budget["daily_limit_usd"] * 100)

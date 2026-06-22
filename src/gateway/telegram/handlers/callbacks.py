"""InlineKeyboard callback 處理。"""
from __future__ import annotations

import httpx
from telegram import Update
from telegram.ext import ContextTypes


def _api(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.bot_data.get("api_base", "http://127.0.0.1:33333")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel":
        await query.edit_message_text("❌ 已取消")

    elif data.startswith("assign:"):
        # assign:issue_id:agent_id
        parts = data.split(":")
        issue_id, agent_id = parts[1], parts[2]
        if agent_id == "auto":
            # 自動選第一個 worker
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{_api(context)}/api/agents")
                agents = r.json()
            workers = [a for a in agents if a.get("role") == "worker"]
            agent_id = workers[0]["id"] if workers else ""

        if agent_id:
            async with httpx.AsyncClient(timeout=10) as c:
                await c.patch(f"{_api(context)}/api/issues/{issue_id}/assign",
                              json={"assignee": agent_id})
            await query.edit_message_text(
                f"✅ 已指派 <b>#{issue_id}</b> → {agent_id}\n⏳ 開始執行...",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text("⚠️ 無可用 Agent")

    elif data.startswith("stop_confirm:"):
        agent_name = data.split(":", 1)[1]
        await query.edit_message_text(f"⏹️ 已發送中斷指令給 {agent_name}")

    elif data.startswith("agent_detail:"):
        agent_id = data.split(":", 1)[1]
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{_api(context)}/api/agents/{agent_id}")
        if r.status_code == 200:
            a = r.json()
            text = (
                f"🤖 <b>{a['name']}</b>\n\n"
                f"角色: {a['role']}\n"
                f"Provider: {a['provider']}\n"
                f"狀態: {a['status']}\n"
                f"模型: {a['model']}\n"
                f"目錄: {a['working_dir']}"
            )
            await query.edit_message_text(text, parse_mode="HTML")

    elif data == "refresh_board":
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{_api(context)}/api/issues")
        from gateway.telegram.formatters import fmt_board
        await query.edit_message_text(fmt_board(r.json()), parse_mode="HTML")

    elif data == "new_issue":
        await query.edit_message_text("請用 /assign 描述 來建立新任務")

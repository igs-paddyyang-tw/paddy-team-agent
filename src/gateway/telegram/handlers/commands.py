"""Telegram 指令 handlers — 11 個 slash 指令。"""
from __future__ import annotations

import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from gateway.telegram.formatters import fmt_status, fmt_board, fmt_costs, fmt_queue


def _api(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.bot_data.get("api_base", "http://127.0.0.1:33333")


async def _get(context: ContextTypes.DEFAULT_TYPE, path: str) -> dict | list:
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{_api(context)}{path}")
        return r.json()


async def _post(context: ContextTypes.DEFAULT_TYPE, path: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{_api(context)}{path}", json=data)
        return r.json()


# ── /start ──

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 歡迎使用 <b>Ark Agent Platform</b>\n\n"
        "我是你的 AI 團隊管理助手，可以幫你：\n"
        "• 派工給 Agent（/assign 描述）\n"
        "• 查看團隊狀態（/status）\n"
        "• 追蹤費用（/costs）\n"
        "• 管理佇列（/queue）\n\n"
        "輸入 /help 查看所有指令"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ── /help ──

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 <b>指令列表</b>\n\n"
        "/status — 團隊即時狀態\n"
        "/agents — Agent 列表\n"
        "/board — 看板摘要\n"
        "/costs — 費用報告\n"
        "/queue — 待處理佇列\n"
        "/assign &lt;描述&gt; — 建立任務並派工\n"
        "/stop &lt;agent&gt; — 中斷執行\n"
        "/retry &lt;issue_id&gt; — 重試任務\n"
        "/logs &lt;agent&gt; — 查看日誌\n"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ── /status ──

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agents = await _get(context, "/api/agents")
    stats = await _get(context, "/api/admin/dashboard/stats")
    text = fmt_status(agents, stats)
    await update.message.reply_text(text, parse_mode="HTML")


# ── /agents ──

async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agents = await _get(context, "/api/agents")
    if not agents:
        await update.message.reply_text("尚無 Agent")
        return
    buttons = []
    for a in agents:
        icon = {"idle": "🟢", "busy": "🔵", "offline": "🔴"}.get(a.get("status", "idle"), "⚪")
        buttons.append([InlineKeyboardButton(
            f"{icon} {a['name']} ({a['role']})",
            callback_data=f"agent_detail:{a['id']}"
        )])
    await update.message.reply_text(
        "🤖 <b>Agent 列表</b>（點擊查看詳情）",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ── /board ──

async def cmd_board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issues = await _get(context, "/api/issues")
    text = fmt_board(issues)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ 新任務", callback_data="new_issue"),
        InlineKeyboardButton("🔄 重新整理", callback_data="refresh_board"),
    ]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


# ── /costs ──

async def cmd_costs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await _get(context, "/api/admin/costs")
    text = fmt_costs(data)
    await update.message.reply_text(text, parse_mode="HTML")


# ── /queue ──

async def cmd_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issues = await _get(context, "/api/admin/queue")
    text = fmt_queue(issues)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎯 批量指派", callback_data="batch_assign"),
    ]]) if issues else None
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


# ── /assign ──

async def cmd_assign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/assign", "").strip()
    if not text:
        await update.message.reply_text("用法：/assign 任務描述\n例如：/assign 建立 REST API")
        return

    # 先建立 Issue
    issue = await _post(context, "/api/issues", {"title": text})

    # 顯示 Agent 選擇
    agents = await _get(context, "/api/agents")
    buttons = [[InlineKeyboardButton(
        f"{a['name']}", callback_data=f"assign:{issue['id']}:{a['id']}"
    )] for a in agents if a.get("role") != "admin"]
    buttons.append([InlineKeyboardButton("🤖 自動判斷", callback_data=f"assign:{issue['id']}:auto")])

    await update.message.reply_text(
        f"📋 已建立 <b>#{issue['id']}</b> — {text}\n\n指派給誰？",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ── /stop ──

async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.replace("/stop", "").strip()
    if not arg:
        await update.message.reply_text("用法：/stop agent_name")
        return
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("⚠️ 確認中斷", callback_data=f"stop_confirm:{arg}"),
        InlineKeyboardButton("取消", callback_data="cancel"),
    ]])
    await update.message.reply_text(f"確定要中斷 <b>{arg}</b>？", parse_mode="HTML", reply_markup=kb)


# ── /retry ──

async def cmd_retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.replace("/retry", "").strip()
    if not arg:
        await update.message.reply_text("用法：/retry issue_id")
        return
    # Reset issue status
    async with httpx.AsyncClient(timeout=10) as c:
        await c.patch(f"{_api(context)}/api/issues/{arg}/assign",
                      json={"assignee": ""})
    await update.message.reply_text(f"🔄 已重新排入佇列：#{arg}")


# ── /logs ──

async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.replace("/logs", "").strip()
    if not arg:
        await update.message.reply_text("用法：/logs agent_name")
        return
    sessions = await _get(context, f"/api/admin/sessions?agent_id={arg}&limit=3")
    if not sessions:
        await update.message.reply_text(f"📝 {arg} 尚無執行記錄")
        return
    lines = [f"📝 <b>{arg} 最近記錄</b>\n"]
    for s in sessions[:3]:
        output = (s.get("output") or "")[:200]
        lines.append(f"• {s.get('started_at', '')[:16]} — {output or '(無輸出)'}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")



# ── /restart ──

async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """重啟 agent 或平台。限 allowed_users。"""
    # 權限檢查
    allowed = context.bot_data.get("allowed_users", [])
    if allowed and update.effective_user.id not in allowed:
        await update.message.reply_text("⛔ 無權限執行此操作")
        return

    arg = update.message.text.replace("/restart", "").strip()
    if not arg:
        await update.message.reply_text("用法：/restart <agent_name|all|platform>")
        return

    agents = context.bot_data.get("agents", {})

    if arg == "platform":
        await update.message.reply_text("🔄 平台重啟中...")
        from pathlib import Path
        Path("restart.flag").touch()
        import sys
        sys.exit(0)
    elif arg == "all":
        for name, agent in agents.items():
            await agent.kill()
            await agent.start()
        await update.message.reply_text(f"✅ 已重啟全部 {len(agents)} 個 Agent")
    elif arg in agents:
        await agents[arg].kill()
        await agents[arg].start()
        await update.message.reply_text(f"✅ 已重啟 {arg}")
    else:
        await update.message.reply_text(f"❌ 找不到 Agent: {arg}")

"""訊息格式化 — 5 種卡片模板。"""
from __future__ import annotations


def fmt_status(agents: list[dict], stats: dict) -> str:
    """狀態卡片。"""
    icons = {"admin": "⚙️", "leader": "🧠", "worker": "💻"}
    status_icons = {"idle": "🟢", "busy": "🔵", "offline": "🔴", "executing": "🔵"}
    lines = ["🤖 <b>Agent Team Status</b>", "━━━━━━━━━━━━━━━━━━━"]
    for a in agents:
        icon = icons.get(a.get("role", "worker"), "💻")
        si = status_icons.get(a.get("status", "idle"), "⚪")
        lines.append(f"{icon} {a['name']:14s}│ {si} {a.get('status', 'idle')}")
    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 完成 {stats.get('completed_today', 0)} │ "
                 f"進行中 {stats.get('running_tasks', 0)}")
    lines.append(f"💰 ${stats.get('total_cost_today_usd', 0):.2f}")
    return "\n".join(lines)


def fmt_completed(issue: dict, agent_name: str, duration_s: float, cost: float) -> str:
    """任務完成通知。"""
    return (
        f"✅ <b>任務完成</b>\n\n"
        f"📋 #{issue.get('id', '')} — {issue.get('title', '')}\n"
        f"🤖 {agent_name}\n"
        f"⏱️ 耗時: {duration_s:.0f} 秒\n"
        f"💰 消耗: ${cost:.4f}\n"
    )


def fmt_board(issues: list[dict]) -> str:
    """看板摘要。"""
    running = [i for i in issues if i.get("status") == "assigned"]
    pending = [i for i in issues if i.get("status") == "pending"]
    completed = [i for i in issues if i.get("status") == "completed"]

    lines = ["📋 <b>Board</b>", "━━━━━━━━━━━━━━━━━━━"]

    if running:
        lines.append(f"\n🔵 <b>進行中</b> ({len(running)})")
        for i in running[:5]:
            lines.append(f"├ #{i['id']} {i['title']} → {i.get('assignee', '?')}")

    if pending:
        lines.append(f"\n🟡 <b>待處理</b> ({len(pending)})")
        for i in pending[:5]:
            p = ["", "🔴", "🟠", "🔵", "⚪"][min(i.get("priority", 3), 4)]
            lines.append(f"├ #{i['id']} {i['title']} {p}")

    if completed:
        lines.append(f"\n✅ <b>已完成</b> ({len(completed)})")

    return "\n".join(lines)


def fmt_costs(data: dict) -> str:
    """費用報告。"""
    lines = [
        "💰 <b>Cost Report</b>",
        "━━━━━━━━━━━━━━━━━━━",
        f"總費用: ${data.get('total_usd', 0):.4f}",
        f"紀錄數: {data.get('total_records', 0)}",
        "",
        "📊 按 Agent:",
    ]
    for agent, cost in list(data.get("by_agent", {}).items())[:5]:
        lines.append(f"├ {agent}: ${cost:.4f}")
    if data.get("by_model"):
        lines.append("\n📊 按 Model:")
        for model, cost in list(data.get("by_model", {}).items())[:3]:
            lines.append(f"├ {model}: ${cost:.4f}")
    return "\n".join(lines)


def fmt_blocker(agent_name: str, issue: dict, message: str) -> str:
    """Blocker 通知。"""
    return (
        f"🚫 <b>Blocker 回報</b>\n\n"
        f"🤖 {agent_name} 執行 #{issue.get('id', '')} 時遇到阻塞：\n\n"
        f"「{message}」"
    )


def fmt_queue(issues: list[dict]) -> str:
    """待處理佇列。"""
    if not issues:
        return "📋 佇列為空 — 所有任務已處理完畢 ✨"
    priority_icons = {1: "🔴", 2: "🟠", 3: "🔵", 4: "⚪"}
    lines = [f"📋 <b>Queue</b> ({len(issues)} 待處理)", ""]
    for i in issues[:10]:
        p = priority_icons.get(i.get("priority", 3), "⚪")
        assignee = f" → {i['assignee']}" if i.get("assignee") else ""
        lines.append(f"{p} #{i['id']} {i['title']}{assignee}")
    if len(issues) > 10:
        lines.append(f"\n... 還有 {len(issues) - 10} 項")
    return "\n".join(lines)

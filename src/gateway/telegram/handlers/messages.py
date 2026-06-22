"""自然語言路由 — @mention + 關鍵字觸發 + 即時回饋。"""
from __future__ import annotations

import asyncio
import logging
import re

import httpx
from telegram import ReactionTypeEmoji, Update
from telegram.ext import ContextTypes

log = logging.getLogger(__name__)

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m|\x1b\[\?[0-9]*[hl]|\x1b\[[0-9]*[A-Z]")

# ── 工具/過程行的特徵 pattern ──
_TOOL_LINE_PREFIXES = (
    "Searching the web", "Reading content from", "Fetching URL",
    "Fetching ", "(using tool:", "✓ Found", "✓ Read",
    "- Completed in", "- Found", "- Read",
    "⏺ ", "┃ ", "│ ", "├ ", "└ ",
    "Running ", "Executed ", "Created ", "Updated ",
    "Tool call:", "Function:", "Calling tool",
)
_TOOL_LINE_RE = re.compile(
    r"^\s*[✓✗●◉⏺]\s+(Found|Read|Completed|Fetched|Searching|Writing|Created)"
    r"|^\s*━+\s*$"
    r"|^\s*─+\s*$"
    r"|^```"
    r"|^\s*\d+\s*(file|match)"
)


def _extract_conclusion(raw: str) -> str:
    """從 kiro-cli 完整輸出中提取最終結論，過濾工具執行過程。

    策略：
    1. 有 [DONE] 標記 → 直接用 summary
    2. 有 reply() 工具輸出 → 提取 reply 內容
    3. 否則從尾部反向掃描，找到最後一段「非工具過程」的連續文字
    """
    # 先清 ANSI
    text = _ANSI_RE.sub("", raw)

    # 策略 1: [DONE] 標記
    done_match = re.search(r"\[DONE\]\s*summary=(.+)", text)
    if done_match:
        return done_match.group(1).strip()

    # 策略 2: 提取最後一個 reply() 呼叫的內容
    # reply(text="...") 或 reply("...")
    reply_matches = re.findall(
        r'reply\s*\(\s*(?:text\s*=\s*)?["\'](.+?)["\']',
        text, re.DOTALL
    )
    if reply_matches:
        return reply_matches[-1].strip()

    # 策略 3: 從尾部提取結論段落
    lines = text.splitlines()

    # 反向找到最後的「結論區塊」— 連續非工具行
    conclusion_lines: list[str] = []
    found_content = False

    for line in reversed(lines):
        stripped = line.strip()

        # 跳過尾部空行
        if not stripped and not found_content:
            continue

        # 偵測工具/過程行
        is_tool_line = (
            any(stripped.startswith(p) for p in _TOOL_LINE_PREFIXES)
            or bool(_TOOL_LINE_RE.match(stripped))
        )

        if is_tool_line:
            if found_content:
                break  # 遇到工具行，結論段落結束
            continue  # 還沒找到內容，繼續往上

        found_content = True
        # Strip kiro-cli '> ' prompt prefix
        if line.startswith("> "):
            line = line[2:]
        conclusion_lines.append(line)

    conclusion_lines.reverse()
    result = "\n".join(conclusion_lines).strip()

    # 若提取結果太短（可能整段都是結論或都是過程），fallback 取最後 2000 字元
    if len(result) < 20 and len(text.strip()) > 20:
        # 做基礎清理後取尾部
        cleaned_lines = []
        for l in lines:
            s = l.strip()
            if not s:
                cleaned_lines.append("")
                continue
            if any(s.startswith(p) for p in _TOOL_LINE_PREFIXES):
                continue
            if _TOOL_LINE_RE.match(s):
                continue
            if l.startswith("> "):
                l = l[2:]
            cleaned_lines.append(l)
        result = "\n".join(cleaned_lines).strip()
        # 取尾部（避免過長）
        if len(result) > 2000:
            result = result[-2000:]

    # 清理多餘空行
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def _api(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.bot_data.get("api_base", "http://127.0.0.1:33333")


KEYWORD_ROUTES = [
    (["狀態", "status", "誰在線"], "status"),
    (["費用", "cost", "花了多少"], "costs"),
    (["看板", "board", "進度"], "board"),
    (["佇列", "queue", "待處理"], "queue"),
]


async def _set_reaction(msg, emoji: str) -> None:
    try:
        await msg.set_reaction(reaction=[ReactionTypeEmoji(emoji=emoji)])
    except Exception:
        pass


async def _keep_action_alive(chat_id: int, action: str, done: asyncio.Event, bot) -> None:
    try:
        while not done.is_set():
            await bot.send_chat_action(chat_id=chat_id, action=action)
            try:
                await asyncio.wait_for(done.wait(), timeout=4.0)
            except asyncio.TimeoutError:
                pass
    except (asyncio.CancelledError, Exception):
        pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理非指令的自然語言訊息。智慧路由：簡單→Gemini / 複雜→Agent。"""
    if not update.message or not update.message.text:
        return
    msg = update.message
    text = msg.text.strip()

    # 關鍵字快速路由
    for keywords, cmd in KEYWORD_ROUTES:
        if any(kw in text.lower() for kw in keywords):
            from gateway.telegram.handlers.commands import (
                cmd_status, cmd_costs, cmd_board, cmd_queue)
            handlers = {"status": cmd_status, "costs": cmd_costs,
                        "board": cmd_board, "queue": cmd_queue}
            await handlers[cmd](update, context)
            return

    # ── 智慧路由：判斷簡單 vs 複雜 ──
    # 複雜任務特徵：@mention、含「建立/實作/修改/測試/部署」等動作詞、超過 100 字
    is_complex = (
        text.startswith("@")
        or len(text) > 100
        or any(kw in text for kw in ["建立", "實作", "修改", "測試", "部署", "設計", "規劃",
                                      "build", "create", "implement", "fix", "deploy", "refactor"])
    )

    if not is_complex:
        # 簡單問題 → Gemini 秒回
        try:
            from gateway.gemini_chat import gemini_chat
            reply = await gemini_chat(text, system="你是 AI 團隊助理，用繁體中文簡潔回答。")
            if reply:
                await msg.reply_text(reply[:4000])
                # 記錄到 memory
                try:
                    from coordinator.a2a.memory_search import MemorySearch
                    ms = MemorySearch()
                    ms.index_turn(msg.from_user.id, "user", text)
                    ms.index_turn(msg.from_user.id, "assistant", reply[:500])
                except Exception:
                    pass
                return
        except Exception as e:
            log.debug("Gemini fallback to agent: %s", e)
            # Gemini 不可用 → 繼續走 Agent

    # ── 即時回饋 ──
    await _set_reaction(msg, "👀")
    done = asyncio.Event()
    timer_task = asyncio.create_task(
        _keep_action_alive(msg.chat_id, "typing", done, context.bot)
    )

    try:
        # 解析 @mention
        mention_match = re.match(r"@([\w-]+)\s*(.*)", text, re.DOTALL)
        if mention_match:
            agent_name = mention_match.group(1)
            message = mention_match.group(2).strip() or text
        else:
            agent_name = None
            message = text

        # 找目標 agent
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{_api(context)}/api/agents")
            agents = r.json()

        target = None
        if agent_name:
            for a in agents:
                if agent_name in a["name"] or agent_name == a["id"]:
                    target = a["id"]
                    break
        if not target:
            leaders = [a for a in agents if a.get("role") == "leader"]
            target = leaders[0]["id"] if leaders else (agents[0]["id"] if agents else None)

        if not target:
            done.set()
            timer_task.cancel()
            await _set_reaction(msg, "❌")
            await msg.reply_text("⚠️ 無可用 Agent")
            return

        # ── 直接呼叫 agent.send() 等待結果 ──
        agent_proc = context.bot_data.get("agents", {}).get(target)
        if not agent_proc:
            done.set()
            timer_task.cancel()
            await _set_reaction(msg, "❌")
            await msg.reply_text("⚠️ Agent 不可用")
            return

        # Mark to suppress duplicate _tg_reply
        handled: set = context.bot_data.get("handled_agents", set())
        handled.add(target)
        try:
            result = await agent_proc.send(message)
        finally:
            handled.discard(target)

        # ── 結案 ──
        done.set()
        timer_task.cancel()

        if result:
            # 提取結論（過濾工具過程與推理步驟）
            result = _extract_conclusion(result)

            if not result:
                result = "✅ 處理完成（無文字輸出）"

            await _set_reaction(msg, "✅")
            log.info("Reply to user: %s", result[:100])
            # 限制長度，避免 TG 洗版
            if len(result) > 3000:
                result = result[-3000:]
            for i in range(0, len(result), 4000):
                await msg.reply_text(result[i:i+4000])
        else:
            await _set_reaction(msg, "❌")
            await msg.reply_text("⚠️ Agent 處理超時或失敗")

    except Exception as e:
        done.set()
        timer_task.cancel()
        await _set_reaction(msg, "❌")
        log.error("handle_message error: %s", e)
        await msg.reply_text(f"⚠️ 處理失敗：{type(e).__name__}")

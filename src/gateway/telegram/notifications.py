"""NotificationService — EventBus 事件 → Telegram 推送。"""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram.ext import Application

from coordinator.events.types import Event, EventType
from gateway.telegram.formatters import fmt_completed, fmt_blocker

log = logging.getLogger("notifications")


class NotificationService:
    """訂閱 EventBus 事件，推送到 Telegram。"""

    # 通知等級：info 只推摘要，warn/error 推完整
    LEVEL_INFO = "info"
    LEVEL_WARN = "warn"
    LEVEL_ERROR = "error"

    def __init__(self, bot_app: "Application", chat_ids: list[int]):
        self.bot = bot_app.bot
        self.chat_ids = chat_ids
        self._throttle: dict[str, float] = {}
        self._min_interval = 1.0  # 秒，防止 TG 限流

    async def on_task_completed(self, event: Event) -> None:
        data = event.data
        output = data.get("output", "")
        summary = output[:200] + "..." if len(output) > 200 else output
        text = (
            f"✅ <b>任務完成</b>\n\n"
            f"📋 #{data.get('issue_id', '?')}\n"
            f"📝 {summary}"
        )
        await self._broadcast(text, self.LEVEL_INFO)

    async def on_task_failed(self, event: Event) -> None:
        data = event.data
        text = (
            f"❌ <b>任務失敗</b>\n\n"
            f"📋 #{data.get('issue_id', '?')}\n"
            f"原因: {data.get('output', 'unknown')[:500]}"
        )
        await self._broadcast(text, self.LEVEL_ERROR)

    async def on_blocker(self, event: Event) -> None:
        data = event.data
        text = fmt_blocker(
            data.get("agent_id", "?"),
            {"id": data.get("issue_id", "?")},
            data.get("message", "未知阻塞"),
        )
        await self._broadcast(text, self.LEVEL_ERROR)

    async def on_budget_warning(self, event: Event) -> None:
        data = event.data
        text = (
            f"⚠️ <b>預算警報</b>\n\n"
            f"今日費用已達 {data.get('percentage', '?')}%\n"
            f"${data.get('today_total', 0):.2f} / ${data.get('limit', 30):.2f}"
        )
        await self._broadcast(text)

    async def on_agent_stopped(self, event: Event) -> None:
        data = event.data
        text = f"🔴 <b>{data.get('agent_id', '?')}</b> 已停止"
        await self._broadcast(text)

    async def on_system_restart(self, event: Event) -> None:
        data = event.data
        text = (
            f"🔄 <b>自動重啟</b>\n\n"
            f"Agent: {data.get('agent_id', '?')}\n"
            f"離線: {data.get('offline_seconds', 0):.0f}s\n"
            f"重啟次數: #{data.get('restart_count', 0)}"
        )
        await self._broadcast(text)

    async def _broadcast(self, text: str, level: str = "info") -> None:
        """發送到所有訂閱的 chat_id。"""
        for chat_id in self.chat_ids:
            try:
                await asyncio.sleep(0.5)  # 節流
                await self.bot.send_message(
                    chat_id=chat_id, text=text, parse_mode="HTML"
                )
            except Exception as e:
                log.warning("通知發送失敗 chat=%s: %s", chat_id, e)

    def subscribe_to(self, bus) -> None:
        """註冊到 EventBus。"""
        bus.subscribe(EventType.TASK_COMPLETED, self.on_task_completed)
        bus.subscribe(EventType.TASK_FAILED, self.on_task_failed)
        bus.subscribe(EventType.TASK_BLOCKER, self.on_blocker)
        bus.subscribe(EventType.BUDGET_WARNING, self.on_budget_warning)
        bus.subscribe(EventType.AGENT_STOPPED, self.on_agent_stopped)
        bus.subscribe(EventType.SYSTEM_RESTART, self.on_system_restart)
        log.info("NotificationService 已訂閱 6 種事件")

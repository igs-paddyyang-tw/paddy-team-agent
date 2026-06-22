"""Progress 更新器 — edit_message 即時刷新進度條。"""
from __future__ import annotations

import asyncio
import logging
import time

log = logging.getLogger("progress")


class ProgressTracker:
    """追蹤單一任務的進度，透過 edit_message 即時更新。"""

    def __init__(self, bot, chat_id: int, message_id: int, agent_name: str, total_steps: int = 4):
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.agent_name = agent_name
        self.total_steps = total_steps
        self.current_step = 0
        self.steps: list[str] = []
        self._last_edit: float = 0
        self._min_interval = 2.0  # TG 限制：同一訊息 2 秒內不可重複編輯

    def _progress_bar(self) -> str:
        filled = int(self.current_step / self.total_steps * 10)
        return "■" * filled + "□" * (10 - filled)

    def _render(self) -> str:
        pct = int(self.current_step / self.total_steps * 100)
        lines = [
            f"⏳ <b>{self.agent_name}</b> 執行中",
            "",
            f"[{self._progress_bar()}] {pct}%",
            "",
        ]
        for i, step in enumerate(self.steps):
            if i < self.current_step:
                lines.append(f"✅ {i+1}/{self.total_steps} {step}")
            elif i == self.current_step:
                lines.append(f"🔵 {i+1}/{self.total_steps} {step}...")
            else:
                lines.append(f"⬜ {i+1}/{self.total_steps} {step}")
        return "\n".join(lines)

    async def update(self, step_name: str) -> None:
        """新增一個步驟並更新訊息。"""
        self.steps.append(step_name)
        self.current_step = len(self.steps) - 1
        await self._edit()

    async def step_done(self) -> None:
        """標記當前步驟完成。"""
        self.current_step = len(self.steps)
        await self._edit()

    async def complete(self, summary: str = "") -> None:
        """標記全部完成。"""
        self.current_step = self.total_steps
        text = f"✅ <b>{self.agent_name}</b> 完成"
        if summary:
            text += f"\n\n{summary[:500]}"
        await self._edit_text(text)

    async def fail(self, reason: str = "") -> None:
        """標記失敗。"""
        text = f"❌ <b>{self.agent_name}</b> 失敗"
        if reason:
            text += f"\n\n{reason[:300]}"
        await self._edit_text(text)

    async def _edit(self) -> None:
        """編輯訊息（含節流）。"""
        now = time.time()
        if now - self._last_edit < self._min_interval:
            await asyncio.sleep(self._min_interval - (now - self._last_edit))
        await self._edit_text(self._render())

    async def _edit_text(self, text: str) -> None:
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=text,
                parse_mode="HTML",
            )
            self._last_edit = time.time()
        except Exception as e:
            log.debug("Progress edit failed: %s", e)

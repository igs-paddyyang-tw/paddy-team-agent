"""A2A Router — 核心協調器（整合 Graph + SharedMemory + Discovery）。"""
from __future__ import annotations

import logging
from typing import Callable, Awaitable

from .protocol import TaskHandoff
from .graph import TaskGraph
from .shared_memory import SharedMemory
from .discovery import AgentDiscovery

log = logging.getLogger("a2a.router")


class A2ARouter:
    def __init__(self, graph: TaskGraph, memory: SharedMemory, discovery: AgentDiscovery,
                 spawn_fn: Callable[[str, str], Awaitable[str | None]] | None = None):
        self.graph = graph
        self.memory = memory
        self.discovery = discovery
        self.spawn_fn = spawn_fn  # async (agent_name, message) -> output

    async def dispatch(self, handoff: TaskHandoff) -> None:
        """接收 handoff → 檢查依賴 → 匹配 agent → spawn。"""
        # 寫入 shared memory
        self.memory.write_task(handoff)
        # 加入依賴圖
        self.graph.add_task(handoff)

        # 檢查是否 ready
        if not self.graph.is_ready(handoff.task_id):
            log.info("Task %s queued (waiting for %s)", handoff.task_id, handoff.depends_on)
            return

        await self._execute(handoff)

    async def _execute(self, task: TaskHandoff) -> None:
        # 匹配 agent
        target = task.to_agent
        if target == "auto":
            target = self.discovery.match(task)
            log.info("Auto-matched %s → %s", task.task_id, target)

        # 組裝 context
        context_parts = [task.title]
        if task.context:
            context_parts.append(task.context)
        # 注入依賴的 output
        for dep_id in task.depends_on:
            dep_output = self.graph.get_output(dep_id)
            if dep_output:
                context_parts.append(f"[依賴 {dep_id} 的產出]:\n{dep_output[:500]}")

        message = "\n\n".join(context_parts)

        # Mark running
        self.graph.mark_running(task.task_id)
        self.memory.update_task(task.task_id, status="running")

        # Spawn
        if self.spawn_fn:
            output = await self.spawn_fn(target, message)
            if output:
                await self.on_complete(task.task_id, output)
            else:
                await self.on_failed(task.task_id, "spawn returned None")

    async def on_complete(self, task_id: str, output: str) -> None:
        """任務完成 → 更新圖 → 解鎖下游。"""
        self.memory.update_task(task_id, status="completed", output=output)
        unlocked = self.graph.mark_complete(task_id, output)
        log.info("Task %s completed, unlocked %d downstream", task_id, len(unlocked))
        for next_task in unlocked:
            await self._execute(next_task)

    async def on_failed(self, task_id: str, reason: str) -> None:
        """任務失敗 → 有 loop_back 時進入 FeedbackLoop 自動修復。"""
        task = self.graph.get_task(task_id)
        if task and task.loop_back and self.spawn_fn:
            from .feedback_loop import FeedbackLoop, MaxIterationsExceeded
            log.info("Task %s entering feedback loop (loop_back=%s)", task_id, task.loop_back)
            try:
                output = await FeedbackLoop(self.spawn_fn).run(task, reason)
                await self.on_complete(task_id, output)
                return
            except MaxIterationsExceeded:
                reason = f"feedback loop exhausted ({task.max_iterations} iterations): {reason}"

        self.memory.update_task(task_id, status="failed", output=reason)
        self.graph.mark_failed(task_id, reason)
        log.warning("Task %s failed: %s", task_id, reason[:100])

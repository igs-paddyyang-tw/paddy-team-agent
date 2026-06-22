"""Feedback Loop — 自動 fix → retest 迴圈。"""
from __future__ import annotations

import logging
from typing import Callable, Awaitable

from .protocol import TaskHandoff

log = logging.getLogger("a2a.feedback")


class MaxIterationsExceeded(Exception):
    pass


class FeedbackLoop:
    def __init__(self, spawn_fn: Callable[[str, str], Awaitable[str | None]]):
        self.spawn_fn = spawn_fn

    async def run(self, task: TaskHandoff, failure_reason: str) -> str:
        """執行 fix → retest 迴圈，最多 max_iterations 次。"""
        executor = task.to_agent
        reviewer = task.loop_back
        if not reviewer:
            raise ValueError("No loop_back agent specified")

        reason = failure_reason
        for i in range(task.max_iterations):
            log.info("Feedback loop %s: iteration %d/%d", task.task_id, i + 1, task.max_iterations)

            # Fix
            fix_msg = f"修復任務：{task.title}\n\n問題（第 {i+1} 次）：{reason}\n\n原始需求：{task.acceptance_criteria}"
            fix_result = await self.spawn_fn(executor, fix_msg)
            if not fix_result:
                reason = "executor returned empty"
                continue

            # Review
            review_msg = f"驗證修復：{task.title}\n\n修復結果：{fix_result[:1000]}\n\n驗收條件：{task.acceptance_criteria}"
            review_result = await self.spawn_fn(reviewer, review_msg)

            if review_result and any(kw in review_result.upper() for kw in ["PASS", "通過", "[DONE]"]):
                log.info("Feedback loop %s: PASSED at iteration %d", task.task_id, i + 1)
                return fix_result

            reason = review_result or "review failed"
            log.info("Feedback loop %s: iteration %d FAILED: %s", task.task_id, i + 1, reason[:100])

        log.warning("Feedback loop %s: max iterations exceeded", task.task_id)
        raise MaxIterationsExceeded(f"{task.task_id}: {reason[:200]}")

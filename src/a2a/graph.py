"""TaskGraph — DAG 任務依賴圖。"""
from __future__ import annotations

from .protocol import TaskHandoff


class CycleError(Exception):
    pass


class TaskGraph:
    def __init__(self):
        self._tasks: dict[str, TaskHandoff] = {}
        self._status: dict[str, str] = {}  # pending/running/completed/failed
        self._outputs: dict[str, str] = {}

    def add_task(self, task: TaskHandoff) -> None:
        if task.task_id in self._tasks:
            return
        # Cycle detection
        if self._has_cycle(task.task_id, task.depends_on):
            raise CycleError(f"Adding {task.task_id} would create a cycle")
        self._tasks[task.task_id] = task
        self._status[task.task_id] = "pending"

    def _has_cycle(self, new_id: str, deps: list[str]) -> bool:
        visited = set()
        def dfs(tid):
            if tid == new_id:
                return True
            if tid in visited:
                return False
            visited.add(tid)
            t = self._tasks.get(tid)
            if t:
                return any(dfs(d) for d in t.depends_on)
            return False
        return any(dfs(d) for d in deps)

    def is_ready(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        return all(self._status.get(d) == "completed" for d in task.depends_on)

    def mark_running(self, task_id: str) -> None:
        self._status[task_id] = "running"

    def mark_complete(self, task_id: str, output: str = "") -> list[TaskHandoff]:
        self._status[task_id] = "completed"
        self._outputs[task_id] = output
        return self._get_unlocked()

    def mark_failed(self, task_id: str, reason: str = "") -> None:
        self._status[task_id] = "failed"
        self._outputs[task_id] = reason

    def get_task(self, task_id: str) -> TaskHandoff | None:
        return self._tasks.get(task_id)

    def get_ready_tasks(self) -> list[TaskHandoff]:
        return [t for tid, t in self._tasks.items()
                if self._status[tid] == "pending" and self.is_ready(tid)]

    def get_output(self, task_id: str) -> str:
        return self._outputs.get(task_id, "")

    def _get_unlocked(self) -> list[TaskHandoff]:
        return [t for tid, t in self._tasks.items()
                if self._status[tid] == "pending" and self.is_ready(tid)]

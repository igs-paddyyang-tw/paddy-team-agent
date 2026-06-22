"""Shared Memory — 檔案系統共享記憶（tasks + artifacts + decisions）。"""
from __future__ import annotations

from pathlib import Path
from .protocol import TaskHandoff
import yaml


class SharedMemory:
    def __init__(self, base: Path = Path("knowledge/shared")):
        self.base = base
        for d in ("tasks", "artifacts", "decisions", "agent_profiles"):
            (self.base / d).mkdir(parents=True, exist_ok=True)

    def write_task(self, task: TaskHandoff) -> None:
        path = self.base / "tasks" / f"{task.task_id}.md"
        content = f"""---
task_id: {task.task_id}
status: pending
assigned_to: {task.to_agent}
depends_on: {task.depends_on}
created_by: {task.from_agent}
priority: {task.priority}
---
# {task.title}

## Context
{task.context[:500]}

## Deliverables
{chr(10).join(f'- [ ] {d}' for d in task.deliverables)}

## Acceptance Criteria
{task.acceptance_criteria}
"""
        path.write_text(content, encoding="utf-8")

    def update_task(self, task_id: str, status: str = "", output: str = "") -> None:
        path = self.base / "tasks" / f"{task_id}.md"
        if not path.exists():
            return
        content = path.read_text(encoding="utf-8")
        if status:
            content = content.replace("status: pending", f"status: {status}")
            content = content.replace("status: running", f"status: {status}")
        if output:
            content += f"\n## Output\n{output[:1000]}\n"
        path.write_text(content, encoding="utf-8")

    def get_task_context(self, task_id: str) -> str:
        path = self.base / "tasks" / f"{task_id}.md"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def write_artifact(self, name: str, content: str) -> Path:
        path = self.base / "artifacts" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def get_agent_profiles(self) -> list[dict]:
        profiles = []
        for f in (self.base / "agent_profiles").glob("*.yaml"):
            profiles.append(yaml.safe_load(f.read_text(encoding="utf-8")))
        return profiles

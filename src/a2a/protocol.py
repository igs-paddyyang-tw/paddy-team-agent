"""A2A Protocol — TaskHandoff + Progress 資料結構。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TaskHandoff:
    """Agent 間任務交接標準格式。"""
    task_id: str
    from_agent: str
    to_agent: str              # "auto" = 自動匹配
    title: str
    context: str = ""          # ≤500 字摘要
    input_artifacts: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    acceptance_criteria: str = ""
    priority: int = 3          # 1=urgent 2=high 3=normal 4=low
    depends_on: list[str] = field(default_factory=list)
    loop_back: str | None = None    # 完成後回傳給誰（feedback loop）
    max_iterations: int = 3
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ProgressEvent:
    """進度事件（從 agent stdout 解析）。"""
    type: str          # progress / artifact / blocker / done / fail
    agent_id: str = ""
    task_id: str = ""
    step: int = 0
    total_steps: int = 0
    message: str = ""
    path: str = ""     # artifact 路徑
    artifacts: list[str] = field(default_factory=list)
    reason: str = ""   # fail 原因

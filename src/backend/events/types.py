"""事件型別定義 — 14 種事件。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EventType(str, Enum):
    # Agent lifecycle
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_OUTPUT = "agent.output"
    AGENT_BUSY = "agent.busy"
    # Task lifecycle
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_BLOCKER = "task.blocker"
    # Cost
    COST_RECORDED = "cost.recorded"
    BUDGET_WARNING = "budget.warning"
    # System
    HEALTH_CHECK = "system.health_check"
    SYSTEM_RESTART = "system.restart"
    SYSTEM_ERROR = "system.error"


@dataclass
class Event:
    type: EventType
    data: dict = field(default_factory=dict)
    source: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

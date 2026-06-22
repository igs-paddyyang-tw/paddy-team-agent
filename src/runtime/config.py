from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class InstanceConfig:
    working_directory: str = "."
    description: str = ""
    role: str = "worker"
    model: str = "auto"
    backend: str = "kiro"  # kiro / gemini / claude
    skip_resume: bool = False
    private_chat: int | None = None

@dataclass
class TeamConfig:
    name: str = "Agent Team"
    instances: dict[str, InstanceConfig] = field(default_factory=dict)
    health_port: int = 13030
    model: str = "auto"
    channel: dict = field(default_factory=dict)
    access: dict = field(default_factory=dict)
    cost_guard: dict = field(default_factory=dict)
    hang_detector: dict = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)

    @property
    def timeout_seconds(self) -> int:
        """從 hang_detector.timeout_minutes 計算超時秒數，預設 3600s。"""
        minutes = self.hang_detector.get("timeout_minutes", 60)
        return int(minutes) * 60

def load_config(path: str | Path) -> TeamConfig:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    instances = {}
    for name, cfg in data.get("instances", {}).items():
        instances[name] = InstanceConfig(
            working_directory=cfg.get("working_directory", "."),
            description=cfg.get("description", ""),
            role=cfg.get("role", "worker"),
            model=cfg.get("model", data.get("defaults", {}).get("model", "auto")),
            backend=cfg.get("backend", data.get("defaults", {}).get("backend", "kiro")),
            skip_resume=cfg.get("skip_resume", False),
            private_chat=cfg.get("private_chat"),
        )
    return TeamConfig(
        name=data.get("name", "Agent Team"),
        instances=instances,
        health_port=data.get("health_port", 13030),
        model=data.get("defaults", {}).get("model", "auto"),
        channel=data.get("channel", {}),
        access=data.get("access", {}),
        cost_guard=data.get("cost_guard", {}),
        hang_detector=data.get("hang_detector", {}),
        examples=data.get("examples", []),
    )

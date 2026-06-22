"""Agent Discovery — 能力匹配（根據 skills + load 自動選 agent）。"""
from __future__ import annotations

from .protocol import TaskHandoff
from .shared_memory import SharedMemory


class AgentDiscovery:
    def __init__(self, memory: SharedMemory):
        self.memory = memory
        # 同義詞映射（英文關鍵字 → 對應中文 skill）
        self._synonyms = {
            "ai-dev-agent": ["ai", "llm", "prompt", "rag", "agent", "ml", "embedding", "設計"],
            "coder-agent": ["api", "fastapi", "express", "python", "typescript", "code", "implement", "build", "開發", "實作"],
            "qa-agent": ["test", "pytest", "review", "security", "audit", "quality", "bug", "測試", "驗證"],
        }

    def match(self, task: TaskHandoff) -> str:
        """根據 task title/context 匹配最佳 agent。"""
        profiles = self.memory.get_agent_profiles()
        if not profiles:
            return task.to_agent

        text_lower = (task.title + " " + task.context).lower()
        scores: list[tuple[str, float]] = []

        for p in profiles:
            if p.get("role") in ("admin", "leader"):
                continue
            score = 0.0
            # 檢查 profile skills
            for skill in p.get("skills", []):
                if skill.lower() in text_lower:
                    score += 1.0
            # 檢查同義詞
            agent_id = p.get("agent_id", "")
            for synonym in self._synonyms.get(agent_id, []):
                if synonym in text_lower:
                    score += 0.8
            # 負載懲罰
            load = p.get("current_load", 0)
            capacity = p.get("capacity", 3)
            if capacity > 0:
                score *= (1 - (load / capacity) * 0.5)
            scores.append((agent_id, score))

        if not scores:
            return task.to_agent

        scores.sort(key=lambda x: -x[1])
        return scores[0][0] if scores[0][1] > 0 else task.to_agent

from __future__ import annotations
import asyncio
import logging
import time

from .config import TeamConfig, load_config
from .process import AgentProcess
from .mcp_registry import McpRegistry

log = logging.getLogger("daemon")

class CoreDaemon:
    def __init__(self, config_path: str = "team.yaml"):
        self.config = load_config(config_path)
        self.mcp_registry = McpRegistry()
        self._agents: dict[str, AgentProcess] = {}
        self._running = False
        self._last_activity: dict[str, float] = {}
        self._restart_count: dict[str, int] = {}
        self.event_log = None

    async def send_to(self, instance_name: str, message: str) -> bool:
        agent = self._agents.get(instance_name)
        if not agent:
            log.warning("Agent not found: %s", instance_name)
            return False
        result = await agent.send(message)
        if result:
            self._last_activity[instance_name] = time.time()
        return result is not None

    def get_status(self) -> dict:
        status = {}
        for name, agent in self._agents.items():
            status[name] = {
                "alive": agent.is_alive(),
                "role": self.config.instances[name].role if name in self.config.instances else "unknown",
                "last_activity": self._last_activity.get(name, 0),
                "restarts": self._restart_count.get(name, 0),
            }
        return status

    async def _health_check(self) -> None:
        for name, agent in list(self._agents.items()):
            if not agent.is_alive() and self._running:
                log.warning("Agent %s is dead, restarting...", name)
                self._restart_count[name] = self._restart_count.get(name, 0) + 1
                await agent.start()
                self._last_activity[name] = time.time()

    async def shutdown(self) -> None:
        self._running = False
        log.info("Shutting down %d agents...", len(self._agents))
        for name, agent in self._agents.items():
            await agent.kill()
        log.info("All agents stopped.")

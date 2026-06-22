"""Health Monitor — 定期檢查 Agent 狀態 + 自動重啟。"""
from __future__ import annotations

import asyncio
import logging
import time

from coordinator.db.models import get_async_db, now_iso
from coordinator.events.types import Event, EventType
from coordinator.events.bus import EventBus

log = logging.getLogger("health_monitor")


class HealthMonitor:
    """每 30 秒檢查 Agent 狀態，離線超過閾值自動重啟。"""

    def __init__(self, bus: EventBus, check_interval: int = 30, offline_threshold: int = 300):
        self.bus = bus
        self.check_interval = check_interval
        self.offline_threshold = offline_threshold
        self._task: asyncio.Task | None = None
        self._agent_last_seen: dict[str, float] = {}
        self._restart_count: dict[str, int] = {}

    def report_alive(self, agent_id: str) -> None:
        """Agent 活動時呼叫。"""
        self._agent_last_seen[agent_id] = time.time()

    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop())
        log.info("Health Monitor started (interval=%ds)", self.check_interval)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()

    async def _loop(self) -> None:
        while True:
            await asyncio.sleep(self.check_interval)
            await self._check()

    async def _check(self) -> None:
        now = time.time()
        conn = await get_async_db()
        try:
            cursor = await conn.execute("SELECT id, name, status FROM agents")
            agents = await cursor.fetchall()

            for agent in agents:
                aid = agent[0]
                last_seen = self._agent_last_seen.get(aid, now)
                offline_seconds = now - last_seen

                if offline_seconds > self.offline_threshold:
                    self._restart_count[aid] = self._restart_count.get(aid, 0) + 1
                    log.warning("Agent %s offline %.0fs, restart #%d",
                                aid, offline_seconds, self._restart_count[aid])
                    await self.bus.emit(Event(
                        type=EventType.SYSTEM_RESTART,
                        data={"agent_id": aid, "offline_seconds": offline_seconds,
                               "restart_count": self._restart_count[aid]},
                        source="health_monitor",
                    ))
                    # Reset timer
                    self._agent_last_seen[aid] = now
        finally:
            await conn.close()

        # Emit health check event
        await self.bus.emit(Event(
            type=EventType.HEALTH_CHECK,
            data={"agents_checked": len(agents),
                   "total_restarts": sum(self._restart_count.values())},
            source="health_monitor",
        ))

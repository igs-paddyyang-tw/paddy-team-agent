from __future__ import annotations
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable
import yaml

log = logging.getLogger("scheduler")

class Scheduler:
    def __init__(self, send_fn: Callable, timezone_name: str = "Asia/Taipei", on_schedule: Callable | None = None, event_bus=None):
        self.send_fn = send_fn
        self.timezone_name = timezone_name
        self.on_schedule = on_schedule
        self.event_bus = event_bus
        self._jobs: list[dict] = []
        self._task: asyncio.Task | None = None
        self._running = False

    def load_yaml(self, path: str) -> int:
        p = Path(path)
        if not p.exists():
            return 0
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        self._jobs = data.get("schedules", []) if data else []
        return len(self._jobs)

    def start(self) -> None:
        self._running = True
        self._task = asyncio.ensure_future(self._loop())

    def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()

    async def _loop(self) -> None:
        while self._running:
            await asyncio.sleep(60)
            now = datetime.now()
            for job in self._jobs:
                if not job.get("enabled", True):
                    continue
                if self._should_run(job, now):
                    target = job.get("target", "")
                    prompt = job.get("prompt", "")
                    if target and prompt:
                        log.info("Scheduler triggering: %s", target)
                        if self.on_schedule:
                            self.on_schedule(target)
                        try:
                            await self.send_fn(target, prompt)
                            await self._emit_completed(job, target)
                        except Exception as e:
                            log.error("Scheduler job failed: %s — %s", target, e)
                            await self._emit_failed(job, target, str(e))

    def _should_run(self, job: dict, now: datetime) -> bool:
        cron = job.get("cron", "")
        if not cron:
            return False
        parts = cron.split()
        if len(parts) != 5:
            return False
        minute, hour, dom, mon, dow = parts
        if not self._match(minute, now.minute):
            return False
        if not self._match(hour, now.hour):
            return False
        if not self._match(dom, now.day):
            return False
        if not self._match(mon, now.month):
            return False
        if not self._match(dow, now.isoweekday() % 7):
            return False
        return True

    def _match(self, field: str, value: int) -> bool:
        if field == "*":
            return True
        for part in field.split(","):
            if "-" in part:
                lo, hi = part.split("-", 1)
                if int(lo) <= value <= int(hi):
                    return True
            elif part.startswith("*/"):
                step = int(part[2:])
                if value % step == 0:
                    return True
            else:
                if int(part) == value:
                    return True
        return False

    async def _emit_completed(self, job: dict, target: str) -> None:
        if not self.event_bus:
            return
        from coordinator.events.types import Event, EventType
        await self.event_bus.emit(Event(
            type=EventType.TASK_COMPLETED,
            data={"agent_id": target, "job_name": job.get("name", ""), "source": "scheduler"},
            source="scheduler",
        ))

    async def _emit_failed(self, job: dict, target: str, error: str) -> None:
        if not self.event_bus:
            return
        from coordinator.events.types import Event, EventType
        await self.event_bus.emit(Event(
            type=EventType.TASK_FAILED,
            data={"agent_id": target, "job_name": job.get("name", ""), "error": error, "source": "scheduler"},
            source="scheduler",
        ))

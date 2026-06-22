"""EventBus — asyncio pub/sub 事件匯流排。"""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Callable

from .types import Event, EventType

log = logging.getLogger("eventbus")


class EventBus:
    def __init__(self, maxsize: int = 10000):
        self._subscribers: dict[EventType, list[Callable]] = defaultdict(list)
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=maxsize)
        self._task: asyncio.Task | None = None
        self._ws_clients: list[asyncio.Queue] = []

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: Callable) -> None:
        for et in EventType:
            self._subscribers[et].append(handler)

    async def emit(self, event: Event) -> None:
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            log.warning("EventBus queue full, dropping event: %s", event.type)

    def add_ws_client(self, q: asyncio.Queue) -> None:
        self._ws_clients.append(q)

    def remove_ws_client(self, q: asyncio.Queue) -> None:
        self._ws_clients = [c for c in self._ws_clients if c is not q]

    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop())
        log.info("EventBus started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()

    async def drain(self) -> None:
        """處理佇列中剩餘事件直到清空。"""
        while not self._queue.empty():
            try:
                event = self._queue.get_nowait()
                for handler in self._subscribers.get(event.type, []):
                    try:
                        await handler(event)
                    except Exception as e:
                        log.error("Drain handler error for %s: %s", event.type, e)
            except asyncio.QueueEmpty:
                break
        log.info("EventBus drained")

    async def _loop(self) -> None:
        while True:
            event = await self._queue.get()
            # Dispatch to subscribers
            for handler in self._subscribers.get(event.type, []):
                try:
                    await handler(event)
                except Exception as e:
                    log.error("Handler error for %s: %s", event.type, e)
            # Push to WebSocket clients
            for ws_q in self._ws_clients:
                try:
                    ws_q.put_nowait(event)
                except asyncio.QueueFull:
                    pass

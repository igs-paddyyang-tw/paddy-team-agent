"""EventBus 整合測試 — subscribe / emit / drain / queue full。"""
import asyncio
import pytest
from backend.events.bus import EventBus
from backend.events.types import Event, EventType


@pytest.mark.asyncio
async def test_subscribe_and_emit():
    bus = EventBus()
    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe(EventType.TASK_CREATED, handler)
    await bus.start()
    await bus.emit(Event(type=EventType.TASK_CREATED, data={"id": "t1"}))
    await asyncio.sleep(0.1)
    await bus.stop()

    assert len(received) == 1
    assert received[0].data["id"] == "t1"


@pytest.mark.asyncio
async def test_emit_does_not_trigger_other_subscribers():
    bus = EventBus()
    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe(EventType.TASK_COMPLETED, handler)
    await bus.start()
    await bus.emit(Event(type=EventType.TASK_CREATED, data={}))
    await asyncio.sleep(0.1)
    await bus.stop()

    assert len(received) == 0


@pytest.mark.asyncio
async def test_queue_full_drops_event():
    bus = EventBus(maxsize=1)
    await bus.emit(Event(type=EventType.TASK_CREATED, data={"n": 1}))
    # Queue is full (size=1), next emit should not raise
    await bus.emit(Event(type=EventType.TASK_CREATED, data={"n": 2}))
    assert bus._queue.qsize() == 1


@pytest.mark.asyncio
async def test_drain_processes_remaining_events():
    bus = EventBus()
    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe(EventType.AGENT_OUTPUT, handler)
    # Emit without starting loop — events stay in queue
    await bus.emit(Event(type=EventType.AGENT_OUTPUT, data={"x": 1}))
    await bus.emit(Event(type=EventType.AGENT_OUTPUT, data={"x": 2}))

    assert bus._queue.qsize() == 2
    await bus.drain()
    assert bus._queue.qsize() == 0
    assert len(received) == 2

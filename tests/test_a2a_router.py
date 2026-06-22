"""A2ARouter 整合測試 — dispatch / 依賴解鎖 / on_complete / on_failed。"""
import asyncio
import pytest
from a2a.router import A2ARouter
from a2a.graph import TaskGraph
from a2a.shared_memory import SharedMemory
from a2a.discovery import AgentDiscovery
from a2a.protocol import TaskHandoff


def _make_router(spawn_results: dict[str, str] | None = None):
    """建立 router，spawn_fn 回傳 spawn_results[agent_name] 或 'ok'。"""
    graph = TaskGraph()
    memory = SharedMemory()
    discovery = AgentDiscovery(memory)
    results = spawn_results or {}
    spawned = []

    async def spawn_fn(agent_name: str, message: str) -> str | None:
        spawned.append((agent_name, message))
        return results.get(agent_name, "ok")

    router = A2ARouter(graph, memory, discovery, spawn_fn=spawn_fn)
    return router, spawned


def _task(task_id: str, to_agent: str = "worker", depends_on: list[str] | None = None) -> TaskHandoff:
    return TaskHandoff(
        task_id=task_id, from_agent="leader", to_agent=to_agent,
        title=f"Do {task_id}", depends_on=depends_on or [],
    )


@pytest.mark.asyncio
async def test_dispatch_ready_task():
    router, spawned = _make_router()
    await router.dispatch(_task("t1", to_agent="dev"))
    assert len(spawned) == 1
    assert spawned[0][0] == "dev"


@pytest.mark.asyncio
async def test_dispatch_blocked_task_not_spawned():
    router, spawned = _make_router()
    await router.dispatch(_task("t1"))
    await router.dispatch(_task("t2", depends_on=["t1"]))
    # t2 依賴 t1，但 t1 已被 spawn 並完成 → t2 也被解鎖
    # 因為 spawn_fn 回傳 "ok" → on_complete 觸發 → t2 也執行了
    assert len(spawned) == 2


@pytest.mark.asyncio
async def test_dependency_unlock_chain():
    router, spawned = _make_router()
    # 先加入有依賴的任務（會 queue）
    await router.dispatch(_task("t2", to_agent="qa", depends_on=["t1"]))
    assert len(spawned) == 0  # t2 blocked

    # 加入 t1（ready → 執行 → complete → 解鎖 t2）
    await router.dispatch(_task("t1", to_agent="dev"))
    assert len(spawned) == 2
    assert spawned[1][0] == "qa"


@pytest.mark.asyncio
async def test_on_failed_marks_task():
    router, _ = _make_router(spawn_results={"dev": None})
    # spawn returns None → on_failed
    await router.dispatch(_task("t1", to_agent="dev"))
    assert router.graph._status["t1"] == "failed"

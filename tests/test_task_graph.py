"""TaskGraph 整合測試 — add / ready / complete / cycle detection。"""
import pytest
from a2a.graph import TaskGraph, CycleError
from a2a.protocol import TaskHandoff


def _task(task_id: str, depends_on: list[str] | None = None) -> TaskHandoff:
    return TaskHandoff(
        task_id=task_id, from_agent="test", to_agent="worker",
        title=f"Task {task_id}", depends_on=depends_on or [],
    )


def test_add_and_ready_no_deps():
    g = TaskGraph()
    g.add_task(_task("t1"))
    assert g.is_ready("t1")


def test_not_ready_with_pending_dep():
    g = TaskGraph()
    g.add_task(_task("t1"))
    g.add_task(_task("t2", depends_on=["t1"]))
    assert not g.is_ready("t2")


def test_ready_after_dep_complete():
    g = TaskGraph()
    g.add_task(_task("t1"))
    g.add_task(_task("t2", depends_on=["t1"]))
    g.mark_complete("t1", "done")
    assert g.is_ready("t2")


def test_mark_complete_returns_unlocked():
    g = TaskGraph()
    g.add_task(_task("t1"))
    g.add_task(_task("t2", depends_on=["t1"]))
    g.add_task(_task("t3", depends_on=["t1"]))
    unlocked = g.mark_complete("t1", "ok")
    ids = [t.task_id for t in unlocked]
    assert "t2" in ids
    assert "t3" in ids


def test_cycle_detection():
    g = TaskGraph()
    g.add_task(_task("t1", depends_on=["t2"]))
    with pytest.raises(CycleError):
        g.add_task(_task("t2", depends_on=["t1"]))


def test_get_ready_tasks():
    g = TaskGraph()
    g.add_task(_task("t1"))
    g.add_task(_task("t2"))
    g.add_task(_task("t3", depends_on=["t1"]))
    ready = g.get_ready_tasks()
    ids = [t.task_id for t in ready]
    assert "t1" in ids
    assert "t2" in ids
    assert "t3" not in ids

"""Phase 1 整合測試 — Backend API 全端點驗證。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient
from backend.api.router import app
from backend.db.models import init_db
from backend.events.bus import EventBus

# Setup
init_db()
app.state.bus = EventBus()
client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_agent_crud():
    # Create
    r = client.post("/api/agents", json={"name": "test-bot", "role": "worker"})
    assert r.status_code == 201
    agent = r.json()
    assert agent["name"] == "test-bot"
    aid = agent["id"]

    # Get
    r = client.get(f"/api/agents/{aid}")
    assert r.status_code == 200
    assert r.json()["role"] == "worker"

    # List
    r = client.get("/api/agents")
    assert r.status_code == 200
    assert any(a["id"] == aid for a in r.json())

    # Update
    r = client.patch(f"/api/agents/{aid}", json={"status": "busy"})
    assert r.status_code == 200
    assert r.json()["status"] == "busy"

    # Delete
    r = client.delete(f"/api/agents/{aid}")
    assert r.status_code == 204


def test_issue_lifecycle():
    # Create agent first
    r = client.post("/api/agents", json={"name": "dev", "role": "worker"})
    agent_id = r.json()["id"]

    # Create issue
    r = client.post("/api/issues", json={"title": "Build API", "priority": 1})
    assert r.status_code == 201
    issue = r.json()
    iid = issue["id"]
    assert issue["status"] == "pending"

    # Assign
    r = client.patch(f"/api/issues/{iid}/assign", json={"assignee": agent_id})
    assert r.status_code == 200
    assert r.json()["status"] == "assigned"

    # Complete
    r = client.patch(f"/api/issues/{iid}/complete", json={"status": "completed", "output": "done"})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    assert r.json()["completed_at"] is not None


def test_issue_fail():
    r = client.post("/api/issues", json={"title": "Failing task"})
    iid = r.json()["id"]
    r = client.patch(f"/api/issues/{iid}/complete", json={"status": "failed", "output": "timeout"})
    assert r.status_code == 200
    assert r.json()["status"] == "failed"


def test_issue_filter_by_status():
    r = client.get("/api/issues?status=completed")
    assert r.status_code == 200
    for issue in r.json():
        assert issue["status"] == "completed"


def test_404_agent():
    r = client.get("/api/agents/nonexist")
    assert r.status_code == 404


def test_404_issue():
    r = client.get("/api/issues/nonexist")
    assert r.status_code == 404


if __name__ == "__main__":
    test_health()
    test_agent_crud()
    test_issue_lifecycle()
    test_issue_fail()
    test_issue_filter_by_status()
    test_404_agent()
    test_404_issue()
    print("\n🎉 All 7 tests passed!")

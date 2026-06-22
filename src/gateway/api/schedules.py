"""Schedules API — 排程管理（list/trigger/pause/resume）。"""
from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
import yaml

router = APIRouter()

SCHEDULER_PATH = Path("scheduler.yaml")


def _load_jobs() -> list[dict]:
    if not SCHEDULER_PATH.exists():
        return []
    data = yaml.safe_load(SCHEDULER_PATH.read_text(encoding="utf-8"))
    return data.get("jobs", [])


def _save_jobs(jobs: list[dict]) -> None:
    data = yaml.safe_load(SCHEDULER_PATH.read_text(encoding="utf-8")) if SCHEDULER_PATH.exists() else {}
    data["jobs"] = jobs
    SCHEDULER_PATH.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding="utf-8")


@router.get("")
def list_schedules():
    """列出所有排程。"""
    jobs = _load_jobs()
    return [{"id": j.get("id", f"job-{i}"), "target": j.get("target", ""),
             "cron": j.get("cron", ""), "enabled": j.get("enabled", True),
             "prompt": j.get("prompt", "")[:80]} for i, j in enumerate(jobs)]


@router.post("/{job_id}/pause")
def pause_schedule(job_id: str):
    """暫停排程。"""
    jobs = _load_jobs()
    for j in jobs:
        if j.get("id") == job_id:
            j["enabled"] = False
            _save_jobs(jobs)
            return {"status": "paused", "id": job_id}
    raise HTTPException(404, f"Job {job_id} not found")


@router.post("/{job_id}/resume")
def resume_schedule(job_id: str):
    """恢復排程。"""
    jobs = _load_jobs()
    for j in jobs:
        if j.get("id") == job_id:
            j["enabled"] = True
            _save_jobs(jobs)
            return {"status": "resumed", "id": job_id}
    raise HTTPException(404, f"Job {job_id} not found")


@router.post("/{job_id}/trigger")
async def trigger_schedule(job_id: str, request: Request):
    """立即觸發排程。"""
    jobs = _load_jobs()
    job = next((j for j in jobs if j.get("id") == job_id), None)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")

    # 透過 EventBus 觸發（或直接 send）
    agents = request.app.state.__dict__.get("agents", {})
    target = job.get("target", "")
    if target and target in agents:
        import asyncio
        asyncio.create_task(agents[target].send(job.get("prompt", "")))
        return {"status": "triggered", "id": job_id, "target": target}
    return {"status": "error", "message": f"Agent {target} not available"}

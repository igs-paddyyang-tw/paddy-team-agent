from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from coordinator.db.models import init_db
from coordinator.events.bus import EventBus
from coordinator.events.types import EventType
from gateway.api.agents import router as agents_router
from gateway.api.issues import router as issues_router
from gateway.api.admin import router as admin_router
from gateway.api.costs import router as costs_router
from gateway.api.schedules import router as schedules_router
from gateway.api.ws import router as ws_router
from coordinator.services.cost_tracker import on_agent_output
from coordinator.services.audit_logger import on_any_event

bus = EventBus()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Use externally injected bus if available, otherwise create one
    if hasattr(app.state, "bus") and app.state.bus:
        _bus = app.state.bus
    else:
        _bus = bus
        _bus.subscribe(EventType.AGENT_OUTPUT, on_agent_output)
        for et in EventType:
            _bus.subscribe(et, on_any_event)
        await _bus.start()
        app.state.bus = _bus
    yield
    if not hasattr(app.state, "_external_bus"):
        await _bus.stop()

app = FastAPI(title="Ark Agent Platform", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(issues_router, prefix="/api/issues", tags=["issues"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(costs_router, prefix="/api/costs", tags=["costs"])
app.include_router(schedules_router, prefix="/api/schedules", tags=["schedules"])
app.include_router(ws_router, prefix="/api", tags=["websocket"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

from __future__ import annotations
import asyncio
import json
from dataclasses import asdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/events")
async def ws_events(websocket: WebSocket):
    await websocket.accept()
    bus = websocket.app.state.bus
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    bus.add_ws_client(q)
    try:
        while True:
            event = await q.get()
            await websocket.send_json({"type": event.type.value, "data": event.data,
                                       "source": event.source, "timestamp": event.timestamp})
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        bus.remove_ws_client(q)

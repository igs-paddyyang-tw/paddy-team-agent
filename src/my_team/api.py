"""HTTP API — 處理 agent MCP tool 呼叫（reply/send/status）。"""
from __future__ import annotations

import asyncio
import html as _html_mod
import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

if TYPE_CHECKING:
    from ark_team_core import CoreDaemon
    from .telegram_adapter import TelegramAdapter

log = logging.getLogger(__name__)
app = FastAPI(title="Team API", version="1.0.0")

_daemon: "CoreDaemon | None" = None
_adapter: "TelegramAdapter | None" = None

_CODENAMES = {
    "admin-agent": "⚙ ️ Admin",
    "pm-agent": "🧠 Leader",
    "dev-agent": "💻 Developer",
    "qa-agent": "🧪 QA",
}


def _format_reply_html(instance: str, text: str, style: str = "chat") -> str:
    if style == "report":
        return text
    header = _CODENAMES.get(instance, f"🤖 {instance.replace('-agent', '')}")
    body = _html_mod.escape(text)
    return f"<b>{header}</b>\n{body}"


def init_api(daemon: "CoreDaemon", adapter: "TelegramAdapter") -> None:
    global _daemon, _adapter
    _daemon = daemon
    _adapter = adapter


class SendRequest(BaseModel):
    instance: str
    message: str
    source: str = ""


class ReplyRequest(BaseModel):
    instance: str
    text: str
    kind: str = "primary"
    style: str = "chat"
    topic_id: int | None = None


class LogRequest(BaseModel):
    instance: str
    source: str = ""
    text: str


class SendPhotoRequest(BaseModel):
    instance: str
    photo_path: str
    caption: str = ""
    chat_id: int | None = None
    topic: int | None = None


class SendDocumentRequest(BaseModel):
    instance: str
    file_path: str
    caption: str = ""
    chat_id: int | None = None
    topic: int | None = None


@app.post("/api/send")
async def api_send(req: SendRequest):
    if not _daemon:
        return {"ok": False, "error": "daemon not ready"}
    success = await _daemon.send_to(req.instance, req.message)
    return {"ok": success}


@app.post("/api/reply")
async def api_reply(req: ReplyRequest):
    if not _adapter:
        return {"ok": False, "error": "telegram adapter not ready"}
    if req.kind == "followup":
        log.info("📝 BUFFERED %s (followup)", req.instance)
        return {"ok": True, "buffered": True}
    formatted = _format_reply_html(req.instance, req.text, style=req.style)
    await _adapter._send_reply(formatted, source=req.instance, parse_mode="HTML", topic_id=req.topic_id)
    return {"ok": True}


@app.post("/api/log")
async def api_log(req: LogRequest):
    if not _daemon:
        return {"ok": False, "error": "daemon not ready"}
    leader = next((n for n, ic in _daemon.config.instances.items() if ic.role == "leader"), None)
    if leader:
        await _daemon.send_to(leader, f"[{req.source}] {req.text}")
    return {"ok": True}


@app.post("/api/send_photo")
async def api_send_photo(req: SendPhotoRequest):
    if not _adapter:
        return {"ok": False, "error": "telegram adapter not ready"}
    from pathlib import Path
    photo = Path(req.photo_path)
    if not photo.exists():
        return {"ok": False, "error": f"file not found: {req.photo_path}"}
    await _adapter._send_photo_reply(photo, caption=req.caption, source=req.instance,
                                     chat_id=req.chat_id, topic=req.topic)
    return {"ok": True}


@app.post("/api/send_document")
async def api_send_document(req: SendDocumentRequest):
    if not _adapter:
        return {"ok": False, "error": "telegram adapter not ready"}
    from pathlib import Path
    doc = Path(req.file_path)
    if not doc.exists():
        return {"ok": False, "error": f"file not found: {req.file_path}"}
    await _adapter._send_document_reply(doc, caption=req.caption, source=req.instance,
                                        chat_id=req.chat_id, topic=req.topic)
    return {"ok": True}


@app.get("/api/status")
async def api_status():
    if not _daemon:
        return {"ok": False, "error": "daemon not ready"}
    return _daemon.get_status()


@app.post("/api/restart/{name}")
async def api_restart(name: str):
    if not _daemon:
        return {"ok": False, "error": "daemon not ready"}
    proc = _daemon._agents.get(name)
    if not proc:
        return {"ok": False, "error": f"unknown instance: {name}"}
    await proc.stop()
    await proc.start()
    import time
    _daemon._last_activity[name] = time.time()
    _daemon._restart_count[name] = _daemon._restart_count.get(name, 0) + 1
    return {"ok": True, "instance": name, "status": "restarted"}


async def start_api(host: str = "127.0.0.1", port: int = 13030) -> None:
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()

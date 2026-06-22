from __future__ import annotations
import asyncio
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

log = logging.getLogger("process")

# 預設超時秒數（當沒有注入 config 時使用）
DEFAULT_TIMEOUT = 3600

# kiro-cli token usage 解析（支援多種格式）
_TOKEN_PATTERNS = [
    # "input_tokens: 1234, output_tokens: 5678"
    re.compile(r"input_tokens[:\s]+(\d+).*?output_tokens[:\s]+(\d+)"),
    # "Tokens: 1234 in / 5678 out"
    re.compile(r"[Tt]okens?[:\s]+(\d+)\s*in\s*/\s*(\d+)\s*out"),
    # "Usage: input=1234 output=5678"
    re.compile(r"[Uu]sage.*?input[=:\s]+(\d+).*?output[=:\s]+(\d+)"),
    # JSON-like: {"input_tokens": 1234, "output_tokens": 5678}
    re.compile(r'"input_tokens"[:\s]+(\d+).*?"output_tokens"[:\s]+(\d+)'),
]


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


def parse_token_usage(text: str) -> TokenUsage | None:
    """從 kiro-cli stderr/stdout 解析 token usage，解析失敗回傳 None。"""
    for pattern in _TOKEN_PATTERNS:
        m = pattern.search(text)
        if m:
            return TokenUsage(input_tokens=int(m.group(1)), output_tokens=int(m.group(2)))
    return None


def estimate_token_usage(input_text: str, output_text: str) -> TokenUsage:
    """Fallback：以字元數 / 4 估算 token 數。"""
    return TokenUsage(
        input_tokens=len(input_text) // 4,
        output_tokens=len(output_text) // 4,
    )


class AgentProcess:
    """每次 send() spawn 一個 kiro-cli 進程，忙碌時排隊依序執行。"""

    _shutting_down: bool = False  # 類別層級 shutdown flag

    def __init__(self, name: str, working_dir: str = ".", model: str = "auto",
                 skip_resume: bool = False, backend: str = "kiro"):
        self.name = name
        self.working_dir = working_dir
        self.model = model
        self.backend = backend
        self.skip_resume = skip_resume
        self._running = False
        self._busy = False
        self.on_output: Callable | None = None
        self.event_bus = None  # 注入 EventBus
        self.timeout: int = DEFAULT_TIMEOUT  # 可由外部設定
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None

    # Multi-runtime backend 配置
    BACKENDS = {
        "kiro": lambda self, msg: [
            "kiro-cli", "chat", "--no-interactive", "--trust-all-tools",
            "--model", self.model,
            *([] if self.skip_resume else ["--resume"]),
            msg,
        ],
        "gemini": lambda self, msg: [
            "gemini", "-p", msg, "-m", self.model, "--skip-trust",
        ],
        "claude": lambda self, msg: [
            "claude", "-p", msg, "--model", self.model,
        ],
    }

    def _build_cmd(self, message: str) -> list[str]:
        builder = self.BACKENDS.get(self.backend)
        if not builder:
            builder = self.BACKENDS["kiro"]
        return builder(self, message)

    async def start(self, _retries: int = 3) -> None:
        """標記為可用，啟動佇列消費 worker（失敗 retry 最多 3 次）。"""
        cwd = Path(self.working_dir).resolve()
        cwd.mkdir(parents=True, exist_ok=True)
        for attempt in range(1, _retries + 1):
            try:
                self._running = True
                if self._worker_task and not self._worker_task.done():
                    self._worker_task.cancel()
                self._worker_task = asyncio.create_task(self._queue_worker())
                log.info("Agent %s ready (cwd=%s)", self.name, cwd)
                return
            except Exception as e:
                log.warning("Agent %s start attempt %d/%d failed: %s", self.name, attempt, _retries, e)
                if attempt < _retries:
                    await asyncio.sleep(5)
        log.error("Agent %s failed to start after %d attempts", self.name, _retries)

    async def _queue_worker(self) -> None:
        """持續從佇列取出任務依序執行。"""
        while self._running:
            try:
                text = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            await self._execute(text)
            self._queue.task_done()

    async def send(self, text: str) -> str | None:
        """將訊息加入佇列。忙碌時排隊而非丟棄。Shutdown 時拒絕新任務。"""
        if AgentProcess._shutting_down:
            log.info("%s: rejecting new task during shutdown", self.name)
            return None
        if not self._running:
            return None
        if self._busy:
            log.info("%s is busy, queuing message (queue_size=%d)", self.name, self._queue.qsize() + 1)
            await self._queue.put(text)
            return "queued"
        # 空閒時直接執行
        return await self._execute(text)

    async def _execute(self, text: str) -> str | None:
        """Spawn kiro-cli 處理一則訊息，完成後回傳 output。"""
        self._busy = True
        cwd = Path(self.working_dir).resolve()
        cmd = self._build_cmd(text)
        log.info("Executing %s: %s", self.name, " ".join(cmd[:6]) + "...")

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd),
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
            output = stdout.decode("utf-8", errors="ignore").strip()
            err_text = stderr.decode("utf-8", errors="ignore").strip()

            # 解析 token usage（優先 stderr，其次 stdout，最後 fallback 估算）
            usage = parse_token_usage(err_text) or parse_token_usage(output)
            if not usage:
                usage = estimate_token_usage(text, output)
            self._last_usage = usage

            if output and self.on_output:
                await self.on_output(self.name, output, usage)

            if proc.returncode != 0 and not output:
                log.warning("%s exited %d: %s", self.name, proc.returncode, err_text[:200])
                return None

            log.info("%s completed (%d chars, %d tokens)", self.name, len(output), usage.total)
            # Parse progress markers
            try:
                from coordinator.a2a.progress_parser import parse_output
                progress_events = parse_output(output)
                for pevt in progress_events:
                    pevt.agent_id = self.name
                    if self.event_bus:
                        from coordinator.events.types import Event, EventType
                        await self.event_bus.emit(Event(
                            type=EventType.AGENT_OUTPUT,
                            data={"agent_id": self.name, "progress_type": pevt.type,
                                  "message": pevt.message, "step": pevt.step,
                                  "total_steps": pevt.total_steps, "artifacts": pevt.artifacts},
                            source="a2a_progress",
                        ))
            except ImportError:
                pass
            # Emit event
            if self.event_bus:
                from coordinator.events.types import Event, EventType
                await self.event_bus.emit(Event(
                    type=EventType.AGENT_OUTPUT,
                    data={"agent_id": self.name, "output": output, "model": self.model,
                          "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens},
                    source="process",
                ))
            return output or "done"

        except asyncio.TimeoutError:
            log.error("%s timed out (%ds)", self.name, self.timeout)
            if self.event_bus:
                from coordinator.events.types import Event, EventType
                await self.event_bus.emit(Event(
                    type=EventType.TASK_FAILED,
                    data={"agent_id": self.name, "output": f"timeout ({self.timeout}s)"},
                    source="process",
                ))
            if self.on_output:
                await self.on_output(self.name, f"⚠️ {self.name} 執行超時（{self.timeout} 秒）", None)
            return None
        except Exception as e:
            log.error("%s failed: %s", self.name, e)
            return None
        finally:
            self._busy = False

    def is_alive(self) -> bool:
        return self._running

    async def kill(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

"""Runtime Registry — 多 Runtime 管理 + Provider Adapter。"""
from __future__ import annotations

import asyncio
import logging
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

log = logging.getLogger("runtime.registry")


class RuntimeStatus(StrEnum):
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"


@dataclass
class RuntimeInfo:
    """單一 Runtime 的狀態資訊。"""
    provider: str
    cli_command: str
    status: RuntimeStatus = RuntimeStatus.UNAVAILABLE
    last_heartbeat: str = ""
    consecutive_failures: int = 0


class ProviderAdapter(ABC):
    """Provider Adapter 介面（Strategy Pattern）。"""

    provider_name: str = ""
    cli_command: str = ""

    @abstractmethod
    async def execute(self, agent_id: str, message: str, working_dir: str = ".") -> str | None:
        """執行任務，回傳 output 或 None（失敗）。"""

    def is_installed(self) -> bool:
        """檢查 CLI 是否在 PATH 中。"""
        return shutil.which(self.cli_command) is not None

    async def health_check(self) -> bool:
        """健康檢查（預設：檢查 CLI 存在）。"""
        return self.is_installed()


class KiroCliAdapter(ProviderAdapter):
    """Kiro CLI Provider。"""
    provider_name = "kiro-cli"
    cli_command = "kiro-cli"

    async def execute(self, agent_id: str, message: str, working_dir: str = ".") -> str | None:
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_command, "chat", "--no-interactive", "-m", message,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            return stdout.decode("utf-8", errors="ignore") if proc.returncode == 0 else None
        except (asyncio.TimeoutError, FileNotFoundError) as e:
            log.error("KiroCli execute failed: %s", e)
            return None


class ClaudeCodeAdapter(ProviderAdapter):
    """Claude Code Provider。"""
    provider_name = "claude-code"
    cli_command = "claude"

    async def execute(self, agent_id: str, message: str, working_dir: str = ".") -> str | None:
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_command, "-p", message, "--output-format", "text",
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=180)
            return stdout.decode("utf-8", errors="ignore") if proc.returncode == 0 else None
        except (asyncio.TimeoutError, FileNotFoundError) as e:
            log.error("ClaudeCode execute failed: %s", e)
            return None


class CodexAdapter(ProviderAdapter):
    """Codex CLI Provider。"""
    provider_name = "codex"
    cli_command = "codex"

    async def execute(self, agent_id: str, message: str, working_dir: str = ".") -> str | None:
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_command, "-q", message,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=180)
            return stdout.decode("utf-8", errors="ignore") if proc.returncode == 0 else None
        except (asyncio.TimeoutError, FileNotFoundError) as e:
            log.error("Codex execute failed: %s", e)
            return None


# ── Provider 註冊表 ──

def _load_providers() -> dict[str, type[ProviderAdapter]]:
    providers: dict[str, type[ProviderAdapter]] = {
        "kiro-cli": KiroCliAdapter,
        "claude-code": ClaudeCodeAdapter,
        "codex": CodexAdapter,
    }
    try:
        from runtime.multica_provider import MulticaProvider
        providers["multica"] = MulticaProvider
    except Exception:
        pass
    return providers

ALL_PROVIDERS: dict[str, type[ProviderAdapter]] = _load_providers()


class RuntimeRegistry:
    """統一管理所有 Runtime，auto-detect + fallback。"""

    def __init__(self) -> None:
        self._runtimes: dict[str, RuntimeInfo] = {}
        self._adapters: dict[str, ProviderAdapter] = {}

    async def auto_detect(self) -> dict[str, RuntimeInfo]:
        """掃描 PATH，偵測可用 CLI。"""
        for name, cls in ALL_PROVIDERS.items():
            adapter = cls()
            installed = adapter.is_installed()
            status = RuntimeStatus.AVAILABLE if installed else RuntimeStatus.UNAVAILABLE
            self._runtimes[name] = RuntimeInfo(
                provider=name,
                cli_command=adapter.cli_command,
                status=status,
                last_heartbeat=datetime.now(timezone.utc).isoformat() if installed else "",
            )
            if installed:
                self._adapters[name] = adapter
                log.info("Runtime detected: %s (%s)", name, adapter.cli_command)
        return self._runtimes

    def resolve(self, provider: str) -> ProviderAdapter | None:
        """取得指定 provider 的 adapter，不可用時 fallback。"""
        # 優先使用指定的
        if provider in self._adapters:
            rt = self._runtimes[provider]
            if rt.status == RuntimeStatus.AVAILABLE:
                return self._adapters[provider]
        # Fallback: 找第一個 available
        for name, rt in self._runtimes.items():
            if rt.status == RuntimeStatus.AVAILABLE and name in self._adapters:
                log.info("Fallback: %s → %s", provider, name)
                return self._adapters[name]
        return None

    def get_all_status(self) -> list[dict]:
        """回傳所有 runtime 狀態（供 API 使用）。"""
        return [
            {
                "provider": rt.provider,
                "cli_command": rt.cli_command,
                "status": rt.status.value,
                "last_heartbeat": rt.last_heartbeat,
            }
            for rt in self._runtimes.values()
        ]

    async def heartbeat(self) -> None:
        """健康檢查所有 runtime（每 30 秒呼叫一次）。"""
        for name, adapter in self._adapters.items():
            rt = self._runtimes[name]
            try:
                ok = await adapter.health_check()
                if ok:
                    rt.status = RuntimeStatus.AVAILABLE
                    rt.last_heartbeat = datetime.now(timezone.utc).isoformat()
                    rt.consecutive_failures = 0
                else:
                    rt.consecutive_failures += 1
                    if rt.consecutive_failures >= 3:
                        rt.status = RuntimeStatus.UNAVAILABLE
            except Exception:
                rt.consecutive_failures += 1
                if rt.consecutive_failures >= 3:
                    rt.status = RuntimeStatus.UNAVAILABLE

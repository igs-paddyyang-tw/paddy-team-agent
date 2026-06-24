"""MulticaProvider — 透過 Multica CLI/API 執行任務（外部 Runtime）。"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil

from runtime.registry import ProviderAdapter

log = logging.getLogger("runtime.multica")


class MulticaProvider(ProviderAdapter):
    """Multica CLI 作為外部 Runtime Provider。

    前置條件：multica CLI 已安裝 + multica setup 完成。
    適用場景：本地 CLI 不可用時 fallback、需要雲端 GPU、跨團隊協作。
    """

    provider_name = "multica"
    cli_command = "multica"

    def __init__(self, workspace_id: str = "") -> None:
        self.workspace_id = workspace_id

    def is_installed(self) -> bool:
        return shutil.which(self.cli_command) is not None

    async def execute(self, agent_id: str, message: str, working_dir: str = ".") -> str | None:
        """透過 multica issue create + 等待完成。"""
        if not self.is_installed():
            log.warning("multica CLI not found")
            return None

        # Step 1: 建立 issue
        issue_id = await self._create_issue(message, agent_id)
        if not issue_id:
            return None

        # Step 2: Polling 等待完成（最多 5 分鐘）
        return await self._wait_for_completion(issue_id, timeout=300)

    async def _create_issue(self, title: str, assignee: str) -> str | None:
        """multica issue create → 回傳 issue_id。"""
        try:
            cmd = [self.cli_command, "issue", "create", "--title", title[:200]]
            if self.workspace_id:
                cmd.extend(["--workspace", self.workspace_id])
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode == 0:
                # Parse issue ID from output
                output = stdout.decode("utf-8").strip()
                # Multica CLI 回傳格式：Created issue: <id>
                if "issue" in output.lower():
                    parts = output.split()
                    return parts[-1] if parts else None
                return output.split("\n")[0].strip()
            return None
        except (asyncio.TimeoutError, FileNotFoundError) as e:
            log.error("multica issue create failed: %s", e)
            return None

    async def _wait_for_completion(self, issue_id: str, timeout: int = 300) -> str | None:
        """Polling issue status 直到完成或超時。"""
        elapsed = 0
        interval = 10
        while elapsed < timeout:
            status = await self._get_issue_status(issue_id)
            if status == "completed":
                return f"Multica issue {issue_id} completed"
            if status == "failed":
                return None
            await asyncio.sleep(interval)
            elapsed += interval
        log.warning("multica issue %s timed out after %ds", issue_id, timeout)
        return None

    async def _get_issue_status(self, issue_id: str) -> str:
        """查詢 issue 狀態。"""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_command, "issue", "list", "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
            if proc.returncode == 0:
                issues = json.loads(stdout.decode("utf-8"))
                for issue in issues:
                    if str(issue.get("id")) == str(issue_id):
                        return issue.get("status", "unknown")
            return "unknown"
        except Exception:
            return "unknown"

    async def health_check(self) -> bool:
        """確認 multica daemon 正在執行。"""
        if not self.is_installed():
            return False
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_command, "daemon", "status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            return proc.returncode == 0
        except Exception:
            return False

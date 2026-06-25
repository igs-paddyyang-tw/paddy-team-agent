"""Wiki Watcher — 監聽 knowledge/raw/ 變動，自動觸發 ingest。"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

log = logging.getLogger("wiki_watcher")

WATCH_INTERVAL = 300  # 每 5 分鐘掃描一次
KNOWLEDGE_DIRS = [
    Path("knowledge/raw"),
]


class WikiWatcher:
    """定期掃描 raw/ 目錄，偵測新檔案後觸發 ingest。"""

    def __init__(self, ingest_fn=None) -> None:
        self.ingest_fn = ingest_fn
        self._known_files: set[str] = set()
        self._initialized = False

    async def start(self) -> None:
        """啟動監聽迴圈。"""
        # 初始化：記錄目前已有的檔案
        self._known_files = self._scan_all()
        self._initialized = True
        log.info("WikiWatcher started, tracking %d existing files", len(self._known_files))

        while True:
            await asyncio.sleep(WATCH_INTERVAL)
            await self._check()

    async def _check(self) -> None:
        """掃描新增檔案。"""
        current = self._scan_all()
        new_files = current - self._known_files

        if new_files:
            log.info("WikiWatcher: %d new files detected", len(new_files))
            for f in sorted(new_files):
                log.info("  + %s", f)

            if self.ingest_fn:
                try:
                    await self.ingest_fn(list(new_files))
                except Exception as e:
                    log.error("Ingest failed: %s", e)

            self._known_files = current

    def _scan_all(self) -> set[str]:
        """掃描所有監聽目錄的 .md 檔案。"""
        files: set[str] = set()
        for d in KNOWLEDGE_DIRS:
            if d.exists():
                for f in d.rglob("*.md"):
                    files.add(str(f))
        # 也掃描各 agent 的 raw/
        agents_dir = Path("agents")
        if agents_dir.exists():
            for raw in agents_dir.glob("*/knowledge/raw/*.md"):
                files.add(str(raw))
        return files

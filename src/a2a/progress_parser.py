"""Progress Parser — 解析 agent stdout 中的 5 種標記。"""
from __future__ import annotations

import re
from .protocol import ProgressEvent

PATTERNS = {
    "progress": re.compile(r"\[PROGRESS\]\s*step=(\d+)/(\d+)\s+msg=(.+)"),
    "artifact": re.compile(r"\[ARTIFACT\]\s*path=(\S+)\s+msg=(.+)"),
    "blocker":  re.compile(r"\[BLOCKER\]\s*need=(\S+)\s+msg=(.+)"),
    "done":     re.compile(r"\[DONE\]\s*summary=(.+?)(?:\s+artifacts=(\S+))?$"),
    "fail":     re.compile(r"\[FAIL\]\s*reason=(\S+)\s+msg=(.+)"),
}


def parse_line(line: str) -> ProgressEvent | None:
    """解析一行 stdout，回傳 ProgressEvent 或 None。"""
    line = line.strip()
    for kind, pattern in PATTERNS.items():
        m = pattern.match(line)
        if not m:
            continue
        if kind == "progress":
            return ProgressEvent(type="progress", step=int(m.group(1)),
                                 total_steps=int(m.group(2)), message=m.group(3))
        elif kind == "artifact":
            return ProgressEvent(type="artifact", path=m.group(1), message=m.group(2))
        elif kind == "blocker":
            return ProgressEvent(type="blocker", reason=m.group(1), message=m.group(2))
        elif kind == "done":
            artifacts = m.group(2).split(",") if m.group(2) else []
            return ProgressEvent(type="done", message=m.group(1), artifacts=artifacts)
        elif kind == "fail":
            return ProgressEvent(type="fail", reason=m.group(1), message=m.group(2))
    return None


def parse_output(text: str) -> list[ProgressEvent]:
    """解析完整 output，回傳所有 ProgressEvent。"""
    events = []
    for line in text.splitlines():
        evt = parse_line(line)
        if evt:
            events.append(evt)
    return events

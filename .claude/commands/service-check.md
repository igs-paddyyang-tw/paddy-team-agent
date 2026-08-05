---
description: 服務檢查 — 查詢團隊狀態並回報
allowed-tools: Read, Glob, Bash
---

用 `query_team_status()` 查詢團隊狀態，回報結果。

若 `team` MCP server 未連線，改用本機檢查並明確說明 server 未啟動：

- 監聽狀態：!`ss -ltnp 2>/dev/null | grep -c ':33333' || echo 0`（1 = 有監聽）
- pid 檔：!`ls /home/paddyyang/kiro-cli/projects/paddy-team-agent/team.pid 2>/dev/null || echo "無 team.pid"`

回報 ≤ 100 字。

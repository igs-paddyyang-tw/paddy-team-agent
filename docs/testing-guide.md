# Phase 1-4 功能測試指南

> 驗證 ai-team-agent 的任務生命週期、多 Runtime、看板 UI、Multica 整合。

## 前置

```bash
cd ai-team-agent
source .venv/bin/activate
python start.py  # 確認 health OK
```

---

## 1. 任務生命週期（Phase 1）

### 1.1 建立任務

```bash
curl -X POST http://localhost:33333/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Build REST API", "assignee": "coder-agent", "priority": 1}'
```

✅ 預期：回傳 `{"id": "t-xxxxxxxx", "status": "queued"}`

### 1.2 查看看板

```bash
curl -s http://localhost:33333/api/board | python3 -m json.tool
```

✅ 預期：`queued` 陣列中有剛建立的任務

### 1.3 模擬狀態轉移

```bash
# 取得 task_id（從上面回傳的 id）
TASK_ID="t-xxxxxxxx"

# 模擬 Agent claim
curl -X PATCH "http://localhost:33333/api/tasks/$TASK_ID/unblock" \
  -H "Content-Type: application/json" \
  -d '{"actor": "test"}'
# → 應失敗（不是 blocked 狀態）
```

### 1.4 Telegram 測試

在 Telegram 對 Bot 發送：
- `/board` → 看到 Kanban 摘要
- `/unblock t-xxxxxxxx` → 回傳錯誤（狀態不符）
- `/retry t-xxxxxxxx` → 回傳錯誤（狀態不符）

---

## 2. 多 Runtime（Phase 2）

### 2.1 查看 Runtime 狀態

```bash
curl -s http://localhost:33333/api/runtimes | python3 -m json.tool
```

✅ 預期：

```json
[
  {"provider": "kiro-cli", "cli_command": "kiro-cli", "status": "available", ...},
  {"provider": "claude-code", "cli_command": "claude", "status": "unavailable", ...},
  {"provider": "codex", "cli_command": "codex", "status": "unavailable", ...},
  {"provider": "multica", "cli_command": "multica", "status": "unavailable", ...}
]
```

### 2.2 Telegram 測試

- `/runtimes` → 看到 4 個 Runtime 狀態（🟢 kiro-cli、🔴 其他）

---

## 3. Kanban Web UI（Phase 3）

### 3.1 瀏覽器開啟

```
http://localhost:33333/board
```

✅ 預期：
- 暗黑科技風格 Kanban 看板
- 5 個欄位（QUEUED / CLAIMED / EXECUTING / BLOCKED / COMPLETED）
- 右側 Agent Sidebar
- 每 10 秒自動刷新

### 3.2 驗證卡片

如果有任務，應看到：
- 任務標題
- 指派者（@agent-name）
- 相對時間（just now / 5m ago）
- 高優先任務有黃色/紅色邊線

---

## 4. 完整生命週期 E2E

### Python 腳本測試

```bash
python -c "
import asyncio, sys
sys.path.insert(0, 'src')
from coordinator.db.models import init_db, get_async_db, create_task, get_board
from coordinator.task_lifecycle import TaskLifecycle

async def e2e():
    await init_db()
    lc = TaskLifecycle()
    conn = await get_async_db()
    await create_task(conn, 'demo-001', 'Demo task', assignee='coder-agent')
    await conn.close()

    # 完整流程
    assert await lc.transition('demo-001', 'claimed', 'coder-agent')
    assert await lc.transition('demo-001', 'executing', 'coder-agent')
    assert await lc.transition('demo-001', 'completed', 'coder-agent', 'done!')

    conn = await get_async_db()
    board = await get_board(conn)
    assert any(t['id']=='demo-001' for t in board['completed'])
    await conn.close()
    print('✅ E2E passed')

asyncio.run(e2e())
"
```

---

## 5. 快速驗證清單

| # | 測試項 | 指令 | 預期 |
|---|--------|------|------|
| 1 | Health | `curl localhost:33333/api/health` | `{"status":"ok"}` |
| 2 | Board API | `curl localhost:33333/api/board` | JSON 含 7 個狀態 key |
| 3 | Runtimes | `curl localhost:33333/api/runtimes` | 4 個 provider |
| 4 | Web UI | 瀏覽器 `localhost:33333/board` | Kanban 頁面 |
| 5 | TG /board | Telegram 發 `/board` | 看板摘要 |
| 6 | TG /runtimes | Telegram 發 `/runtimes` | Runtime 列表 |
| 7 | 建立任務 | POST /api/tasks | 回傳 task_id |

---

*測試通過後即可正式使用。*

# 團隊運作規範

> 本文件由系統自動產生（policy=always），反映實際權限與團隊組成。

## 團隊成員

| Instance | 角色 | 職責 |
|----------|------|------|
| cto-agent | admin | 👑 技術長 — 服務監控、套件維護、Bug 修復、架構設計（本 workspace） |
| admin-agent | admin | 👑 Admin — 服務管理、開發維護、團隊指揮 |
| leader-agent | leader | 🧠 Leader — 需求分析、派工、驗收 |
| ai-dev-agent | worker | 🤖 AI Dev — AI/ML 架構、Prompt 工程、Agent 設計 |
| coder-agent | worker | 💻 Coder — 全端開發、API 實作、程式碼產出 |
| qa-agent | worker | 🧪 QA — 測試、品質保證、Code Review |

## 指揮鏈

```
使用者 → admin → manager → leader → worker
```

## 跨 Agent 通訊規則

你是 admin，可以發訊息給所有人，無限制。

| 角色 | 可發給 | 可用工具 |
|------|--------|---------|
| admin | 所有人 | send_to_instance / delegate_task / broadcast_all |
| leader | 所有人（除 admin） | send_to_instance / delegate_task / broadcast_all |
| manager | 所有 group 成員 | send_to_instance（無 create_task） |
| worker | leader + 其他 worker | send_to_instance（無 delegate_task / broadcast_all） |

## MCP 工具（你可直接呼叫）

| 工具 | 用途 |
|------|------|
| `reply(text, kind)` | 回覆使用者（Telegram），唯一出口 |
| `query_team_status()` | 查詢團隊狀態 |
| `log_to_leader(text)` | 私下回報火影（錯誤/過程） |
| `list_tasks(status)` | 列出任務板 |
| `update_task(task_id, status, note)` | 更新任務狀態 |
| `record_spend(amount_usd, note)` | 記錄成本消費 |
| `send_to_instance(instance, msg)` | 發訊息給指定 agent |
| `delegate_task(instance, task)` | 委派任務（加格式前綴） |
| `create_task(title, assignee, ...)` | 建立任務到 board.json |
| `broadcast_all(message)` | 廣播訊息給所有 agent |
| `wiki_query(query, scope)` | 搜尋知識庫 |
| `wiki_ingest(source_path, scope)` | 匯入知識 |

## 協作流程

```
leader(spec) → worker(PR) → devops(Review) → qa(QA) → leader(驗收)
```

- 程式碼變更：全走 flow
- 文件/GDD：leader → design → leader 驗收
- 分析報告：leader → analyst → leader 驗收
- 退回單級不跳關，同一關失敗 3 次升級上級

## 成員管理規範

你有權調整團隊成員組成。變更流程：

1. 修改 `team.yaml` 的 `instances` 區塊（新增/移除/改 role）
2. 重啟服務（寫 restart.flag）讓 TEAM.md 自動重新產生
3. 所有 agent 下次啟動時會拿到更新後的成員表

**注意：** TEAM.md 由系統每次啟動自動產生（policy=always），
手動修改會在下次重啟時被覆寫。成員變更一律改 team.yaml。
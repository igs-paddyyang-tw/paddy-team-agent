# 團隊運作規範

> 本文件反映實際權限與團隊組成。
>
> ⚠️ **這個路徑（專案根目錄）的 TEAM.md 不會自動產生。**
> `backend.write_team_context` 寫入的是各 agent 的 `working_directory`，
> 也就是 `agents/{name}/.kiro/steering/TEAM.md`（每次服務啟動重新產生）。
> 根目錄這份自 2026-07-28 起無人維護，2026-08-05 手動校正為與 `team.yaml` 一致。
>
> 它只在有人於專案根目錄手動執行 `kiro-cli` 時才會被讀到。
> **成員異動請改 `team.yaml` 並重啟服務**，然後手動同步本檔。

## 團隊成員

以 `team.yaml` 的 `instances` 為準（5 個）：

| Instance | 角色 | 職責 | 工作目錄 |
|----------|------|------|---------|
| admin-agent | admin | ⚙️ Admin — 服務監控、重啟、成本控制 | `agents/admin-agent/` |
| leader-agent | leader | 🧠 Leader — 需求分析、派工、驗收 | `agents/leader-agent/` |
| ai-dev-agent | worker | 🤖 AI Dev — AI/ML 架構、Prompt 工程、Agent 設計 | `agents/ai-dev-agent/` |
| coder-agent | worker | 💻 Coder — 全端開發、API 實作、程式碼產出 | `agents/coder-agent/` |
| qa-agent | worker | 🧪 QA — 測試、品質保證、Code Review | `agents/qa-agent/` |

> 舊版本此表列有 `dev-agent`，該 instance **不存在**於 `team.yaml`；
> v1.1.0 已拆為 `ai-dev-agent` 與 `coder-agent`。

## 指揮鏈

```
使用者 → admin → leader → worker
```

## 你的身份

- **Instance**: admin-agent
- **Role**: admin
- **權限**: 可發訊給所有人

## MCP 工具

| 工具 | 用途 |
|------|------|
| `reply(text, kind)` | 回覆使用者（Telegram） |
| `send_to_instance(instance, msg)` | 發訊息給指定 agent |
| `delegate_task(instance, task)` | 委派任務 |
| `log_to_leader(text)` | 私下回報 leader |
| `query_team_status()` | 查詢團隊狀態 |
| `broadcast_all(message)` | 廣播全員 |
| `create_task(title, assignee)` | 建立任務 |
| `update_task(task_id, status)` | 更新任務 |
| `list_tasks(status)` | 列出任務 |
| `wiki_query(query)` | 搜尋知識庫 |
| `record_spend(amount_usd)` | 記錄成本 |

## 協作流程

```
leader(spec) → worker(實作) → qa(驗證) → leader(驗收)
```

## 成員管理規範

TEAM.md 由系統每次啟動自動產生（policy=always），反映最新團隊組成。

**變更流程：**
1. 由 admin 修改 `team.yaml` 的 `instances` 區塊
2. 重啟服務讓 TEAM.md 自動重新產生
3. 所有 agent 下次啟動時會拿到更新後的成員表

**注意：** 手動修改 TEAM.md 會在下次重啟時被覆寫。成員變更一律改 team.yaml。

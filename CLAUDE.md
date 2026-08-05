# paddy-team-agent — admin-agent

> **所有回覆使用繁體中文。** 每完成一個段落更新 `.kiro/steering/MEMORY.md`。

@.kiro/steering/SOUL.md
@.kiro/steering/AGENTS.md
@agents/admin-agent/.kiro/steering/TEAM.md
@.kiro/steering/USER.md
@.kiro/steering/MEMORY.md

---

## 為什麼用 `@` 匯入而不是複製

`.kiro/steering/` 是**單一真實來源**，Kiro 與 Claude Code 共用同一份，避免雙軌期間規範分歧。

## ⚠️ `TEAM.md` 有兩份，只有 agent 目錄下的那份是活的

`TEAM.md` 由服務啟動時自動產生（`ark_team_agent.backend.write_team_context`，policy=always），手動修改會被覆寫 — 成員變更一律改 `team.yaml` 後重啟。

**但產生器寫的是每個 agent 自己的 working_directory，不是專案根目錄：**

| 路徑 | 狀態 |
|---|---|
| `agents/{name}/.kiro/steering/TEAM.md` | ✅ **活的** — 每次啟動重新產生，反映 `team.yaml` |
| `.kiro/steering/TEAM.md` | ❌ **孤兒檔** — 最後寫入 2026-07-28，沒有任何機制會更新它 |

根目錄那份仍是 v1.1.0 改名前的舊版（只列 4 個、含不存在的 `dev-agent`），**不要引用它**。本檔的 `@` 匯入已指向 `agents/admin-agent/.kiro/steering/TEAM.md`。

### 讀 TEAM.md 時的注意事項

產生出來的表會多一列 `cto-agent`（標「本 workspace」），那是**套件硬編碼**的（`backend.py` 的 `Always include cto-agent`），代表 workspace 本體而非真的 agent — **paddy 沒有 cto-agent**。以 `team.yaml` 的 5 個為準：

| Instance | role | 工作目錄 |
|---|---|---|
| `admin-agent` | admin | `agents/admin-agent/` |
| `leader-agent` | leader | `agents/leader-agent/`（json 檔名是 `pm-agent.json`，舊命名遺留） |
| `ai-dev-agent` | worker | `agents/ai-dev-agent/` |
| `coder-agent` | worker | `agents/coder-agent/` |
| `qa-agent` | worker | `agents/qa-agent/` |

## Python 程式碼規範

寫 `.py` 前先讀 `.kiro/steering/KIRO.md`。

> 原為 Kiro 的 `inclusion: fileMatch` / `src/**/*.py` 條件載入。本專案 v1.1.0 定版已刪除 `src/`，故不建 `src/CLAUDE.md`。

## 團隊執行

| 項目 | 值 |
|---|---|
| MCP server | `team` @ port 33333（見 `.mcp.json`） |
| 入口 | `.venv/bin/python3 start.py` |
| 團隊組成 | 4 agents：admin / leader / dev / qa |
| 指揮鏈 | 使用者 → admin → leader → worker |
| 套件 | `ark_team_agent` 1.0.1（`.venv`） |

MCP 工具（`reply` / `send_to_instance` / `delegate_task` / `query_team_status` / `broadcast_all` / `wiki_query` 等）需 `team` server 連線後才可用。

## 專案結構

```
paddy-team-agent/
├── .claude/skills/     57 個 ark-* skills（clone，可 git pull 更新）
├── .kiro/              Kiro 配置（steering 為規範單一來源）
├── .mcp.json           team MCP server
├── agents/ tasks/ workflows/ state/ data/
├── knowledge/ docs/ logs/ secrets/ scripts/
├── start.py            服務入口
└── team.yaml           成員設定（TEAM.md 由此產生）
```

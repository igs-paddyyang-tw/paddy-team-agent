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

## `.kiro/` 目錄地圖（做 agent／提詞開發時看這裡）

| 路徑 | 放什麼 | 誰維護 |
|---|---|---|
| `.kiro/steering/*.md` | 行為規範與記憶，Kiro 依 frontmatter 的 `inclusion` 自動載入 | ✋ 手寫 |
| `.kiro/prompts/*.md` | 可重用提詞模板（本專案 2 個），Kiro 內以 `@檔名` 呼叫 | ✋ 手寫 |
| `.kiro/agents/admin-agent.json` | agent 身分註冊檔（本專案僅 `name`/`description`/`role` 三欄） | ✋ 手寫 |
| `.kiro/skills/` | **空的** — v1.1.0 定版時清掉，Kiro 側目前沒有 skill | — |
| `.kiro/hooks/` | 不存在（本專案沒有 hook） | — |
| `.claude/skills/` | 57 個 ark-* skills，外部 clone，已 gitignore | `git pull` |

### 🚨 根目錄的 `.kiro/` 有兩個孤兒檔，執行期都不讀

產生器（`backend.py`）寫入的是**每個 agent 的 `working_directory`**，本專案 admin-agent 的是 `agents/admin-agent`，所以根目錄那份沒人維護也沒人使用：

| 檔案 | 根目錄那份 | 真正在用的 |
|---|---|---|
| `TEAM.md` | ❌ 孤兒（停在 2026-07-28） | `agents/{name}/.kiro/steering/TEAM.md` |
| `settings/mcp.json` | ❌ 孤兒（不被覆寫，也不被讀） | `agents/{name}/.kiro/settings/mcp.json` |

> 兩份都是每次服務啟動時由 `write_team_context` / `_write_mcp_config` 重新產生到 agent 目錄下，**手改 agent 目錄下的版本會被覆寫**。
>
> 改設定的正確位置：成員→`team.yaml`、MCP→`backend.py` 的注入邏輯、排程→`scheduler.yaml`。
>
> 註：根目錄 `.kiro/settings/mcp.json` 曾有 `command: "py"` 與已刪除的 `src/` 路徑（2026-08-05 修正）。因為它是孤兒檔，**Kiro 執行期並未受影響**；修正的實際意義是本專案的 `.mcp.json`（Claude Code 用）由它複製而來。

### 提詞模板格式（`.kiro/prompts/*.md`）

純 Markdown，**無 frontmatter**，直接寫指示；Kiro 內以 `@route-message` 這樣呼叫。

> Claude Code 側的對應是 `.claude/commands/*.md` — 需要 YAML frontmatter（`description`、`argument-hint`），參數用 `$ARGUMENTS`。兩邊格式不同，不能互相複製。

### Agent 註冊檔的 `file://` 陷阱

若要在 `.kiro/agents/*.json` 用 `file://` 引用資源，解析基準是 `.kiro/agents/`，必須往上兩層 —— `file://../../.kiro/steering/SOUL.md`；寫成 `file://.kiro/...` 會失效（踩坑紀錄見 `MEMORY.md`）。

## 團隊執行

| 項目 | 值 |
|---|---|
| 常駐方式 | **systemd user service**（`paddy-team-agent.service`，`Restart=always`） |
| MCP server | `team` @ port 33333（見 `.mcp.json`） |
| 入口 | `.venv/bin/python start.py`（由 systemd 呼叫，不要手動前景執行） |
| 團隊組成 | 5 agents：admin / leader / ai-dev / coder / qa（以 `team.yaml` 為準） |
| 指揮鏈 | 使用者 → admin → leader → worker |
| 套件 | `ark_team_agent` 1.0.1（`.venv`） |

### 服務管理

```bash
systemctl --user status  paddy-team-agent      # 狀態（含 5 個 kiro-cli 子程序）
systemctl --user restart paddy-team-agent      # 改 team.yaml / steering 後重啟
systemctl --user stop    paddy-team-agent
journalctl --user -u paddy-team-agent -f       # 看 log
```

- Unit 檔本體在 `~/.config/systemd/user/paddy-team-agent.service`，版控備份在 `scripts/paddy-team-agent.service`（機器重建時複製回去 → `systemctl --user daemon-reload && systemctl --user enable --now paddy-team-agent`）
- `loginctl enable-linger` 已啟用，登出後服務不中斷
- `PATH` 必須含 `~/.local/bin`（`kiro-cli` 在那裡），unit 檔已寫死
- 與 `aiops` / `director` / `ninja-bot` / `ninja-team` 同一套管理方式

> ⚠️ **不要用 `python start.py` 手動前景啟動** — 會與 systemd 搶 port 33333，且終端關閉即死。

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

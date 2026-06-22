---
title: "AI Team Platform — 四層獨立運作架構"
status: approved
type: spec
version: "2.0"
language: zh-TW
author: paddyyang
created: 2026-06-22
updated: 2026-06-22
supersedes: "v1.0（四層外部依賴版）"
---

# AI Team Platform — 四層獨立運作架構 (v2)

## 1. 設計原則

- **獨立可運行** — 不依賴任何外部服務（Plane/GitHub/OpenClaw）
- **漸進式升級** — 每個功能可選啟用，缺了也能跑
- **零 LLM 路由** — 意圖分類用 keyword，不消耗 token
- **多 Runtime 混合** — 不同 agent 用不同 CLI，快慢兼顧

---

## 2. 架構總覽

```
              User
               │
═══════════════════════════════════════
  Gateway Layer (ai-bot)               ← 入口層：FastAPI + TG Bot
═══════════════════════════════════════
│
├── Telegram Bot (python-telegram-bot)
├── FastAPI HTTP API (port 33333)
├── Auth（白名單 + rate limit）
├── ConversationPlanner（6 層路由）
├── 即時回饋（👀 / typing / ✅ / ❌）
└── Gemini API 快速路徑（簡單問答 2-3s）
               │
═══════════════════════════════════════
  Coordinator Layer (Platform Core)    ← 協調層：派工 + 狀態 + 事件
═══════════════════════════════════════
│
├── Agent Registry                    5 agents + 狀態追蹤
├── Runtime Registry                  kiro/gemini/claude 配置
├── Issue DB + Board                  任務管理（SQLite）
├── Event Bus                         事件解耦
└── Scheduler                         定時排程
               │
═══════════════════════════════════════
  Execution Layer (Multi-Runtime)      ← 執行層：spawn CLI
═══════════════════════════════════════
│
├── AgentProcess (spawn subprocess)
├── Backends:
│   ├── kiro-cli    (深度，有工具鏈)
│   ├── gemini-cli  (快速，對話)
│   └── claude-cli  (程式碼)
└── Fallback Chain: preferred → gemini → kiro → claude → API
               │
═══════════════════════════════════════
  Knowledge Layer                      ← 知識層：記憶 + Skills
═══════════════════════════════════════
│
├── knowledge/ (per agent 私有)
├── skills/ (54 個共用 SKILL.md)
└── .kiro/steering/ (角色定義)
```

---

## 3. 入口層 (Gateway = ai-bot)

ai-bot 就是 Gateway。用 FastAPI + python-telegram-bot 實作，不需獨立服務。

### 3.1 職責

| 職責 | 實作 |
|------|------|
| 接收外部訊息 | TG Bot polling + HTTP endpoint |
| 統一驗證 | 白名單 user ID |
| 統一路由 | ConversationPlanner 六層 |
| 統一回饋 | Reaction + typing + clean output |
| 快速回答 | Gemini API 直連（不進 Coordinator） |

### 3.2 三級回應

| 級別 | 觸發 | 後端 | 延遲 |
|------|------|------|------|
| ⚡ 即時 | keyword / /cmd / 簡單問答 | Gemini API / Python Skill | 1-5s |
| 🔄 標準 | 一般問答（API 不可用） | CLI subprocess | 5-30s |
| 🧠 深度 | 深度關鍵字 / @mention agent | kiro-cli multi-agent | 30-120s |

即時回饋：
- 👀 Reaction → typing → ✅/❌
- 無中間訊息

### 3.2 HTTP API（內部用）

| 端點 | 用途 |
|------|------|
| `GET /api/health` | 健康檢查 |
| `GET /api/agents` | Agent 列表 |
| `POST /api/issues` | 建立任務 |
| `GET /api/admin/dashboard/*` | Dashboard 數據 |

### 3.3 未來可選擴充（不影響核心）

- GitHub App（PR event → Issue）
- Slack/Discord Bot
- Web Chat UI

---

## 4. 協調層 (Platform Core)

### 4.1 ConversationPlanner（意圖路由）

六層路由（零 LLM 消耗）：

```
L1: /reset                          → 重置
L2: /skill_id args                  → Skill 直接執行
L3: keyword → 本地 Skill            → news_scraper / llm_cli / echo
L4: keyword → 直達 team agent       → qa-agent / admin-agent
L5: 深度關鍵字 → pm-agent 派工      → 規劃/分析/架構/重構
L6: 預設 → Gemini API 快速回答      → fallback CLI
```

### 4.2 Agent Registry

```python
# team.yaml instances → DB 同步
agents = {
    "admin-agent": {role: "admin", backend: "kiro", status: "idle"},
    "pm-agent":    {role: "leader", backend: "gemini", status: "idle"},
    "coder-agent": {role: "worker", backend: "kiro", status: "idle"},
    "ai-dev-agent":{role: "worker", backend: "kiro", status: "idle"},
    "qa-agent":    {role: "worker", backend: "kiro", status: "idle"},
}
```

### 4.3 Runtime Registry

```python
BACKENDS = {
    "kiro": {
        "cmd": "kiro-cli",
        "args": ["chat", "--no-interactive", "--trust-all-tools", "--model", "{model}"],
        "capabilities": ["file_write", "git", "mcp_tools", "web_search"],
        "latency": "10-120s",
    },
    "gemini": {
        "cmd": "gemini",
        "args": ["-p", "{prompt}", "-m", "{model}", "--skip-trust"],
        "capabilities": ["web_search", "code_gen"],
        "latency": "5-30s",
    },
    "claude": {
        "cmd": "claude",
        "args": ["-p", "{prompt}", "--model", "{model}"],
        "capabilities": ["code_gen", "analysis"],
        "latency": "5-30s",
    },
}
```

### 4.4 Issue DB + Board

SQLite 內建（`data/platform.db`）：
- `issues` 表：id, title, status, assignee, priority, created_at
- 狀態流：`pending → assigned → completed / failed`
- 無需外部 PM 工具

### 4.5 Event Bus

```
Event Types:
├── AGENT_STARTED / STOPPED
├── AGENT_OUTPUT
├── TASK_CREATED / ASSIGNED / COMPLETED / FAILED
└── SYSTEM_ERROR
```

所有元件透過 EventBus 解耦，不直接呼叫。

### 4.6 Scheduler

APScheduler 驅動：
- `scheduler.yaml` 定義 cron jobs
- 觸發時呼叫 `agent.send(prompt)`

---

## 5. 執行層 (Multi-Runtime)

### 5.1 AgentProcess

每次 `send()` spawn 一個 CLI subprocess：

```python
class AgentProcess:
    def __init__(self, name, working_dir, backend="kiro", model="auto"):
        self.backend = backend  # kiro / gemini / claude

    def _build_cmd(self, message: str) -> list[str]:
        cfg = BACKENDS[self.backend]
        # 組裝 CLI 指令
        ...

    async def send(self, text: str) -> str | None:
        cmd = self._build_cmd(text)
        proc = await asyncio.create_subprocess_exec(*cmd, cwd=self.working_dir)
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=300)
        return clean_output(stdout)
```

### 5.2 team.yaml Backend 配置

```yaml
instances:
  admin-agent:
    backend: kiro          # 需要完整工具鏈
  pm-agent:
    backend: gemini        # 分析+派工，快速回覆
  coder-agent:
    backend: kiro          # 需要寫檔案
  ai-dev-agent:
    backend: kiro          # 需要 MCP 工具
  qa-agent:
    backend: kiro          # 需要跑測試
```

### 5.3 Fallback Chain

```
preferred backend → gemini → kiro → claude → Gemini API 直連 → 靜態回應
```

任何一層不可用自動降級，確保永遠有回覆。

### 5.4 Output 清洗

所有 CLI output 統一清洗後才送到使用者：
- Strip ANSI escape codes
- 過濾工具執行日誌（web_search/Fetching/✓ Found）
- Strip `> ` prompt 前綴
- 提取結論段落（`_extract_conclusion`）

---

## 6. 知識層

### 6.1 Agent 私有知識庫

```
agents/{name}/knowledge/
├── schema.md       # 規則（角色客製化）
├── index.md        # 索引
├── log.md          # 操作日誌（append-only）
├── raw/            # 唯讀原始資料
└── wiki/           # 結構化知識頁面
```

### 6.2 共用 Skills

```
skills/             # 54 個 ark-* Skills
├── ark-superpowers/SKILL.md
├── ark-wiki-engine/SKILL.md
└── ...
```

- 靜態 Markdown 檔案
- auto_discover 掃描並註冊
- 每個 agent 的 `.kiro/skills/` 放子集（8-10 個）

### 6.3 角色定義

```
agents/{name}/.kiro/steering/
├── SOUL.md         # 八段式角色定義
├── AGENTS.md       # 行為準則
├── KIRO.md         # 程式碼規範 + 壓縮策略
├── MEMORY.md       # 專案記憶
├── USER.md         # 使用者偏好
└── TEAM.md         # 團隊成員表
```

---

## 7. 獨立性保證

| 缺失 | 行為 | 影響 |
|------|------|------|
| 無 Gemini API Key | CLI fallback | 簡單問答慢一點（5-30s → 代替 2-3s） |
| 無 kiro-cli | gemini/claude fallback | 失去 file_write/git 能力 |
| 無任何 CLI | Gemini API 直連 | 只能簡單問答 |
| 無 Telegram | HTTP API 仍可用 | curl 觸發任務 |
| 只有 1 agent | 單 agent 模式 | 不派工直接做 |
| 無 Scheduler | 手動觸發 | 無定時任務 |
| 無 EventBus | 同步呼叫 | 失去事件追蹤 |

**核心保證：只要有 1 個 CLI + 1 個 Bot token = 系統可運行。**

---

## 8. 資料流

### 簡單問答（⚡ 2-3s）

```
User → TG Bot → Planner(L6) → gemini_chat(API) → reply
```

### Skill 執行（⚡ 1-5s）

```
User → TG Bot → Planner(L2/L3) → registry.invoke() → reply
```

### Agent 深度處理（🧠 30-120s）

```
User → TG Bot → Planner(L4/L5) → agent.send()
                                      ↓
                              kiro-cli subprocess
                              (cwd=agents/{name}/)
                              (reads .kiro/steering/)
                              (uses .kiro/skills/)
                                      ↓
                              _extract_conclusion()
                                      ↓
                                    reply
```

---

## 9. 與 v1 Spec 差異

| v1 | v2 | 理由 |
|----|-----|------|
| OpenClaw 獨立 Gateway 服務 | ai-bot 就是 Gateway（FastAPI） | 不需額外服務，同一進程 |
| Multica 外部協調服務 | 自建 Coordinator（start.py） | 已有 EventBus + Registry |
| Plane 整合 | 砍掉 — 用 Issue DB | 5 人團隊不需要外部 PM 工具 |
| GitHub Webhook | 砍掉 — agent 直接 git 操作 | kiro-cli 已有 git 能力 |
| Hermes 獨立 Runtime 框架 | 簡化 — CLI subprocess | 不需要獨立服務框架 |
| Skill Review/Publish 流程 | 簡化 — 放 skills/ 就能用 | 小團隊不需正式 review |
| Sprint/Project 管理 | 砍掉 — Issue + Board 就夠 | 不是 Scrum 團隊 |
| Runtime Manager 配額 | 簡化 — cost_guard daily limit | 已有 |

**保留四層分工，砍掉外部依賴。Gateway = ai-bot（FastAPI + TG Bot 同一進程）。**

---

## 10. 實作路徑

| # | 項目 | 基礎 | 改動量 |
|---|------|------|--------|
| 1 | 合併 ai-bot TG handler 到 ai-team-agent | ai-bot 已完整 | ~100 行整合 |
| 2 | process.py 支援 `backend` 欄位 | llm_cli.py 已有邏輯 | ~30 行 |
| 3 | team.yaml + config.py 加 `backend` | 加一個 field | ~5 行 |
| 4 | start.py 注入 Planner + Gemini fast path | 已寫好模組 | ~50 行 |

**總計：~200 行程式碼調整。不需新模組。**

---

## 11. 未來可選擴充

以下為非核心功能，按需加入：

| 功能 | 加入方式 | 優先級 |
|------|---------|--------|
| GitHub App | 加 webhook endpoint + Issue 同步 | P3 |
| Web Dashboard | 啟動 apps/web/ 靜態頁面 | P3 |
| Slack/Discord | 新增 bot adapter | P4 |
| Skill 版本管理 | skills/ 加 git tag | P4 |
| 多團隊（第二個 team） | 不同 port + 不同 team.yaml | P5 |

# AI Team Agent `v1.0.0`

> 5 人 AI Agent 團隊管理平台 — 五層架構 + Multica 級任務管理 + 多 Runtime
>
> 使用 [`ark-agent-team-builder`](skills/ark-agent-team-builder/) `v2.0` 產出

## 版本對應

| ai-team-agent | ark-agent-team-builder | 功能 |
|---------------|----------------------|------|
| v1.0.0 | v2.0 | Phase 1-4 完成（任務生命週期 + 多 Runtime + Kanban + Multica） |

> **版號規則**：`ark-agent-team-builder` 採 `v2.X` 遞增。每次 generator 新增功能時 X+1，ai-team-agent 同步更新對應版本。

## 快速開始

```bash
git clone https://github.com/igs-paddyyang-tw/ai-team-agent.git
cd ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start.py        # 一鍵啟動全平台
```

## 核心功能

| 功能 | 說明 |
|------|------|
| 任務生命週期 | 7 狀態機（BACKLOG→QUEUED→CLAIMED→EXECUTING→BLOCKED/FAILED→COMPLETED） |
| 多 Runtime | auto-detect kiro-cli / claude-code / codex / multica，自動 fallback |
| Kanban Web UI | `http://localhost:33333/board`（暗黑科技風格、10s 自動刷新） |
| Autopilot | cron 排程自動建立任務 + 指定 assignee |
| Telegram 指揮 | /board /assign /unblock /retry /runtimes /costs |

## 五層架構

```
L1 Entry        → API + Telegram + Web Board
L2 OS           → TaskLifecycle + Autopilot + EventBus
L3 Collaboration→ A2A Router + TaskGraph + Agent Discovery
L4 Execution    → RuntimeRegistry + ProviderAdapter (4 providers)
L5 Knowledge    → Wiki + Memory + Skill Evolution
```

```
User ─── Telegram / Web / API ─── Gateway :33333
                                      │
                                  Coordinator
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                     pm-agent    coder-agent    qa-agent
                     (leader)    (worker)       (worker)
```

## 目錄結構

```
ai-team-agent/
├── start.py                     # 入口
├── team.yaml                    # 5 人團隊配置
├── src/
│   ├── gateway/                 # 入口層
│   │   ├── api/                 # REST API（21 端點 + RBAC）
│   │   ├── telegram/            # TG Bot（11 指令 + 通知 + InlineKeyboard）
│   │   └── gemini_chat.py       # Gemini 秒回
│   ├── coordinator/             # 協調層
│   │   ├── a2a/                 # TaskGraph + Discovery + FeedbackLoop
│   │   ├── db/                  # SQLite 7 表
│   │   ├── events/              # EventBus（14 事件）
│   │   └── services/            # cost_tracker + audit_logger + health
│   ├── runtime/                 # 執行層
│   │   ├── process.py           # kiro-cli spawn
│   │   ├── daemon.py            # Agent 管理
│   │   └── scheduler.py         # Cron 排程
│   ├── business/                # 業務技能
│   │   ├── news_scraper.py
│   │   └── news_renderer.py
│   └── bootstrap.py             # 啟動邏輯
├── apps/web/                    # Web Dashboard（Next.js 8 頁面）
├── agents/                      # 5 Agent 工作目錄
├── knowledge/shared/            # A2A 共享記憶
├── docs/                        # Specs + Designs + Plans
├── Dockerfile
└── docker-compose.prod.yml
```

## 團隊

| Agent | Role | 職責 |
|-------|------|------|
| admin-agent | 👑 admin | 服務管理、部署、團隊指揮 |
| pm-agent | 🧠 leader | 需求分析、任務拆解、派工、驗收 |
| ai-dev-agent | 🤖 worker | AI 架構、Prompt 工程、Agent 設計 |
| coder-agent | 💻 worker | 全端開發、API 實作 |
| qa-agent | 🧪 worker | 測試、品質保證、Code Review |

## 功能

### Telegram Bot

```
/status  /agents  /board  /costs  /queue  /assign  /stop  /retry  /logs  /help
```

智慧路由：簡單問題 → Gemini 秒回 / 複雜任務 → Agent 派工

### A2A 協作

- **TaskGraph**：DAG 依賴自動解鎖
- **Discovery**：中英文 skills 匹配最佳 Agent
- **FeedbackLoop**：qa 失敗 → coder 修 → qa 重測（max 3 輪）
- **SharedMemory**：knowledge/shared/ 跨 agent context

### Web Dashboard

```bash
cd apps/web && npm install && npm run dev  # → localhost:3000
```

8 頁面：Dashboard / Agents / Sessions / Costs / Audit / Queue / Settings

## 部署

```bash
docker compose -f docker-compose.prod.yml up -d
```

## 相關 Repos

| Repo | 說明 |
|------|------|
| [ark-agent-skills](https://github.com/igs-paddyyang-tw/ark-agent-skills) | 54 Skills + Builder |
| [ai-workshop](https://github.com/igs-paddyyang-tw/ai-workshop) | 4 個 Workshop 教材 |

## 授權

MIT

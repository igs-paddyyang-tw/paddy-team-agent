# AI Team Agent

> 5 人 AI Agent 團隊管理平台 — Backend API + Telegram Bot + Web Dashboard + A2A 協作

## 快速開始

```bash
git clone https://github.com/igs-paddyyang-tw/ai-team-agent.git
cd ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 TELEGRAM_BOT_TOKEN
python start.py        # 一鍵啟動全平台
```

啟動後：
- Backend API → http://localhost:33333
- Telegram Bot → 對 @你的Bot 發 `/start`
- Web Dashboard → `cd apps/web && npm install && npm run dev` → http://localhost:3000

## 架構

```
User ─── Telegram Bot ─── Backend API :33333 ─── Agent Daemon
              │                 │                     │
              │            EventBus              kiro-cli × 5
              │                 │
              └──── A2A Router ─┘
                    ├── TaskGraph (DAG 依賴)
                    ├── Discovery (能力匹配)
                    ├── SharedMemory (context 傳遞)
                    └── FeedbackLoop (fix → retest)
```

## 團隊配置

| Agent | Role | 職責 |
|-------|------|------|
| admin-agent | 👑 admin | 服務管理、部署、團隊指揮 |
| pm-agent | 🧠 leader | 需求分析、任務拆解、派工、驗收 |
| ai-dev-agent | 🤖 worker | AI 架構、Prompt 工程、Agent 設計 |
| coder-agent | 💻 worker | 全端開發、API 實作、程式碼產出 |
| qa-agent | 🧪 worker | 測試、品質保證、Code Review |

## 功能

### Telegram Bot（11 指令）

```
/status   團隊即時狀態       /assign   派工
/agents   Agent 列表         /costs    費用報告
/board    看板摘要           /queue    待處理佇列
/stop     中斷 Agent         /retry    重試任務
/logs     查看日誌           /help     說明
```

### Backend API（21 端點）

| 域 | 端點 |
|----|------|
| Health | `GET /api/health` |
| Agents | CRUD `/api/agents` |
| Issues | lifecycle `/api/issues` |
| Admin | `/api/admin/dashboard/stats`, `/costs`, `/audit`, `/queue`, `/sessions` |
| WebSocket | `WS /api/ws/events` |

### A2A 協作機制

- **TaskGraph**：DAG 任務依賴（自動解鎖下游）
- **Discovery**：根據 skills 自動匹配最佳 Agent（中英文）
- **SharedMemory**：檔案系統共享 context（knowledge/shared/）
- **FeedbackLoop**：qa 失敗 → coder 修 → qa 重測（max 3 輪）
- **Progress**：`[PROGRESS] [ARTIFACT] [DONE] [FAIL]` 標記即時回報

### Web Dashboard（8 頁面）

```
/admin/dashboard   KPI + 趨勢圖 + Agent 狀態 + 即時事件
/admin/agents      Agent 卡片列表
/admin/sessions    Session 回放（對話 + Tool Call）
/admin/costs       費用分析（Bar + Pie 圖表）
/admin/audit       審計日誌（篩選 + 滾動）
/admin/queue       佇列管理（優先級調整）
/admin/settings    預算設定
```

## 目錄結構

```
ai-team-agent/
├── start.py                 # 統一入口（5 服務）
├── team.yaml                # 團隊配置
├── src/
│   ├── a2a/                 # A2A 協作層（384 行）
│   ├── ark_team_core/       # Agent Runtime
│   ├── backend/             # REST API + EventBus + Services
│   └── tg_ui/              # Telegram Bot
├── apps/web/               # Web Dashboard (Next.js)
├── agents/                 # 5 Agent 工作目錄 + Skills
├── knowledge/shared/       # A2A 共享記憶
├── docs/                   # Specs + Designs + Plans
├── Dockerfile
└── docker-compose.prod.yml
```

## 部署

### Docker

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 環境變數

```bash
TELEGRAM_BOT_TOKEN=your-token
API_PORT=33333
# PLATFORM_API_KEYS=key1:admin,key2:member  (生產模式)
```

## 文件

| 類型 | 檔案 |
|------|------|
| 規格書 | `docs/specs/` — Backend / TG UI / Web / A2A / Builder |
| 設計文件 | `docs/designs/` — Web Dashboard / A2A 協作 |
| 執行計畫 | `docs/plans/` — Platform / Web / A2A / 整合 |

## 技術棧

| 層級 | 技術 |
|------|------|
| Agent Runtime | kiro-cli (spawn mode) |
| Backend | Python / FastAPI / SQLite |
| Telegram | python-telegram-bot 22 |
| Web | Next.js 15 / React 18 / Tailwind / Recharts |
| Event Bus | asyncio pub/sub (14 events) |
| A2A | TaskGraph DAG + Discovery + FeedbackLoop |

## 授權

MIT

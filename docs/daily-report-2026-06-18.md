# 日報：AI Team Agent 專案

> **日期**：2026-06-18（三）
> **撰寫者**：pm-agent
> **專案狀態**：🟢 開發中（MVP 階段）

---

## 一、設計理念

### 核心願景

打造 **5 人 AI Agent 協作平台**，透過 Telegram Bot 作為使用者入口，後端統一調度多個 AI Agent 完成需求分析、開發、測試等任務。

### 設計原則

| 原則 | 說明 |
|------|------|
| Spec-Driven | 先產文件再動手，確保需求可追溯 |
| Event-Driven | EventBus 作為核心中樞，解耦各模組 |
| 全 Python 棧 | FastAPI + python-telegram-bot + kiro-cli，統一技術棧 |
| 漸進式架構 | SQLite 開發 / PostgreSQL 生產，可隨規模升級 |

### 架構總覽

```
User ─── Telegram Bot ─── Backend API :33333 ─── Agent Daemon
              │                 │                     │
              │            SQLite/PostgreSQL       kiro-cli × 5
              │                 │
              └──── EventBus ───┘
```

### 團隊組成（5 個 Agent）

| Agent | 角色 | 職責 |
|-------|------|------|
| admin-agent | 👑 Admin | 服務管理、開發維護 |
| pm-agent | 🧠 Leader | 需求分析、派工、驗收 |
| ai-dev-agent | 🤖 AI Dev | AI/ML 架構、Prompt 工程 |
| coder-agent | 💻 Coder | 全端開發、API 實作 |
| qa-agent | 🧪 QA | 測試、品質保證 |

---

## 二、技術棧

| 層級 | 技術 |
|------|------|
| Telegram UI | python-telegram-bot 22 |
| Backend API | FastAPI + uvicorn |
| Event Bus | asyncio pub/sub |
| Services | Cost Tracker / Audit Logger / Health Monitor |
| Agent Runtime | kiro-cli spawn |
| Database | SQLite (dev) / PostgreSQL (prod) |
| 部署 | Docker Compose |

---

## 三、目前進度

### ✅ 已完成

| 模組 | 狀態 | 說明 |
|------|------|------|
| `src/ark_team_core/` | ✅ 完成 | config / process / daemon / scheduler / mcp_registry |
| `src/backend/db/` | ✅ 完成 | SQLite 初始化 + models |
| `src/backend/events/` | ✅ 完成 | EventBus + EventType 定義 |
| `src/backend/api/` | ✅ 完成 | FastAPI router + agents/issues CRUD |
| `src/backend/services/` | ✅ 完成 | cost_tracker + audit_logger |
| `src/tg_ui/` | ✅ 完成 | Bot 骨架 + handlers + notifications + formatters |
| `src/a2a/` | ✅ 完成 | Agent-to-Agent 協議 + router + shared memory + feedback loop |
| `start.py` | ✅ 完成 | 統一入口（一鍵啟動全平台） |
| `team.yaml` | ✅ 完成 | 團隊配置 |
| 設計文件 | ✅ 完成 | ark-platform-design.md（完整架構） |
| 55 個 Skills | ✅ 完成 | 涵蓋開發、文件、分析等領域 |

### 🟡 已啟動運行

- 平台今日 12:46 啟動成功
- 5 個 Agent 全部就緒
- Scheduler + Telegram Bot + NotificationService 正常運行
- Backend API 在 port 33333 服務中

### 🔴 已知問題（Workshop Report）

| 問題 | 嚴重度 | 狀態 |
|------|--------|------|
| TelegramAdapter `channel` dict vs attribute 存取 | Medium | 已識別待修 |
| 教學包缺少 PEP 668 venv 說明 | Low | 文件補充 |

---

## 四、檔案結構摘要

```
ai-team-agent/
├── src/
│   ├── ark_team_core/    # Agent Runtime（5 模組）
│   ├── backend/          # FastAPI + DB + Events + Services
│   ├── tg_ui/            # Telegram Bot UI
│   ├── a2a/              # Agent-to-Agent 協作協議
│   └── my_team/          # MCP Tools 業務層
├── agents/               # 5 個 Agent 的 .kiro 配置
├── skills/               # 55 個 Skill 定義
├── knowledge/            # Wiki 知識庫
├── docs/                 # 規格書 + 設計文件 + 計畫
├── start.py              # 統一入口
└── team.yaml             # 團隊配置
```

---

## 五、今日重點

1. 平台穩定運行中，全部 5 個 Agent 已就緒
2. A2A（Agent-to-Agent）模組今日更新（feedback_loop、router、shared_memory）
3. process.py 今日有更新（可能是 event emit 強化）

---

## 六、下一步

- [ ] 修復 TelegramAdapter channel 屬性存取 bug
- [ ] 補充 E2E 整合測試
- [ ] 完善 RBAC 權限控制
- [ ] Docker 生產部署驗證
- [ ] 效能壓力測試

---

*本報告由 pm-agent 自動產出 — 2026-06-18 16:40 UTC+8*

---
title: "ai-team-agent 目錄結構優化 — 先 B 後 A 執行計畫"
type: onepager
status: draft
created: 2026-06-22
updated: 2026-06-22
language: zh-TW
author: paddyyang
---

# ai-team-agent 目錄結構優化

## 問題

`start.py` 420+ 行包辦入口/協調/執行，`src/` 下模組命名與四層架構對不上，`state/` vs `data/` 重複，ai-bot 合併後會更混亂。

## 目標

目錄結構反映四層架構，每層職責可見、可獨立測試。

---

## Phase B — 最小改動（1 天）

不改功能，只改組織。改完系統行為不變。

### B1. start.py 拆分

```
Before:
  start.py（420 行，全部邏輯）

After:
  start.py（30 行，只做 import + asyncio.run）
  src/bootstrap.py（啟動順序：DB → Bus → Agents → TG → Scheduler）
```

驗收：`python start.py` 啟動行為不變。

### B2. state/ 合併到 data/

```
Before:
  state/events.db     ← 事件 DB
  data/platform.db    ← 平台 DB
  data/memory.db      ← 記憶 DB

After:
  data/events.db
  data/platform.db
  data/memory.db
  （刪除 state/ 目錄）
```

驗收：相關 import path 更新，DB 正常讀寫。

### B3. src/my_team/ 重命名

```
Before:
  src/my_team/           ← 命名模糊
    ├── news_scraper.py
    ├── news_renderer.py
    ├── tools/
    ├── mcp_setup.py
    ├── api.py
    └── event_log.py

After:
  src/business/          ← 業務邏輯（Gateway 的本地 Skill）
    ├── news_scraper.py
    ├── news_renderer.py
    └── tools/
  src/coordinator/       ← 搬 api.py + event_log.py + mcp_setup.py 到協調層
```

驗收：import 更新，功能不變。

### B4. 根目錄 .kiro/ 精簡

```
Before:
  .kiro/（簡略 3 行 agent.json，與 agents/admin-agent/.kiro 重複）

After:
  .kiro/ → 只保留 Kiro CLI 開發用的 steering/
  刪除 .kiro/agents/admin-agent.json（避免與 agents/ 下的混淆）
  或改為 symlink → agents/admin-agent/.kiro
```

驗收：kiro-cli 在根目錄開啟仍正常。

---

## Phase A — 四層重組（在合併 ai-bot 時一起做，2-3 天）

### A1. src/ 按四層重組

```
src/
├── gateway/              # 入口層（合併 ai-bot + tg_ui）
│   ├── telegram/         #   handlers, notifications, formatters
│   ├── api/              #   FastAPI HTTP endpoints
│   ├── planner.py        #   ConversationPlanner 六層路由
│   ├── feedback.py       #   即時回饋（👀/typing/✅）
│   └── gemini_chat.py    #   Gemini API 快速路徑
│
├── coordinator/          # 協調層（合併 backend + a2a）
│   ├── registry.py       #   Agent + Runtime Registry
│   ├── dispatcher.py     #   Issue → Agent 派工
│   ├── eventbus.py       #   Event Bus
│   ├── scheduler.py      #   APScheduler
│   ├── db/               #   SQLite models + migrations
│   └── a2a/              #   router, memory, feedback_loop, graph
│
├── runtime/              # 執行層（合併 ark_team_core）
│   ├── process.py        #   AgentProcess（multi-backend）
│   ├── config.py         #   team.yaml 解析
│   └── backends.py       #   BACKENDS dict + fallback chain
│
└── business/             # 本地業務 Skills
    ├── news_scraper.py
    └── news_renderer.py
```

### A2. 合併 ai-bot 到 gateway/

```
ai-bot/src/bot/          → src/gateway/telegram/
ai-bot/src/conversation/ → src/gateway/planner.py + session.py
ai-bot/src/llm/          → src/gateway/gemini_chat.py
ai-bot/src/skills/       → src/business/（echo 等本地 Skill）
```

合併後刪除 `ai-bot/` 獨立目錄。

### A3. start.py → src/bootstrap.py 完整版

```python
# start.py（最終版）
import asyncio
from src.bootstrap import main
asyncio.run(main())
```

`bootstrap.py` 按四層順序啟動：
1. Knowledge（DB init）
2. Coordinator（EventBus + Registry + Scheduler）
3. Runtime（AgentProcess × N）
4. Gateway（TG Bot + FastAPI）

### A4. team.yaml 加 backend 欄位

```yaml
instances:
  pm-agent:
    backend: gemini      # 快速對話
  coder-agent:
    backend: kiro        # 需要工具
```

`src/runtime/config.py` 讀取 backend → `process.py` 使用對應 CLI。

---

## 最終目錄結構（Phase A 完成後）

```
ai-team-agent/
├── start.py                # 30 行入口
├── team.yaml               # 團隊配置
├── scheduler.yaml          # 排程
├── src/
│   ├── gateway/            # 入口層
│   ├── coordinator/        # 協調層
│   ├── runtime/            # 執行層
│   └── business/           # 業務 Skills
├── agents/                 # 5 agents workspace
├── skills/                 # 54 共用 Skills（.kiro 用）
├── knowledge/              # 團隊知識庫
├── data/                   # 所有 DB
├── config/                 # YAML 設定
├── templates/              # HTML 模板
├── apps/web/               # Dashboard（Next.js）
├── docs/                   # specs/designs/plans
├── tests/
└── logs/
```

---

## 風險

| 風險 | 緩解 |
|------|------|
| Phase B import 路徑改壞 | 每步改完立刻 `python start.py` 驗證 |
| Phase A 改動大 | 和 ai-bot 合併一起做，一次搞定 |
| agents/ 下的 .kiro skills 路徑失效 | skills 用相對路徑，不受 src/ 重組影響 |
| 正在運行的服務中斷 | Phase B 只改命名，不改邏輯 |

---

## 時程

| Phase | 預估 | 前置 |
|-------|------|------|
| B（最小改動） | 1 天 | 無 |
| A（四層重組 + ai-bot 合併） | 2-3 天 | Phase B 完成 |

**B 可以現在做。A 等你確認 ai-bot 功能正確後一起做。**

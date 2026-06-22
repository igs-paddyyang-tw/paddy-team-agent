---
title: "Ark Agent Platform — 整合計畫"
type: onepager
version: "1.0"
status: completed
language: zh-TW
author: paddyyang
created: 2026-06-17
updated: 2026-06-17
---

# Ark Agent Platform — 整合計畫 One Pager

## 問題

目前系統有三個獨立運行的元件，尚未真正整合：

| 元件 | 狀態 | 問題 |
|------|------|------|
| Agent Daemon（`start.py`） | ✅ 可運行 | 僅 stdin/stdout，無持久化 |
| Backend API（`src/backend/`） | ✅ 通過測試 | 獨立運行，未與 daemon 串接 |
| Telegram Bot（`src/telegram/`） | ✅ 模組完成 | 仍用舊的 TelegramAdapter |

**核心矛盾**：`start.py`（舊入口）和 `start_platform.py`（新入口）並存，TG Bot 有兩套（舊 `my_team/telegram_adapter.py` + 新 `src/telegram/`），使用者不知道該跑哪個。

---

## 目標

**一個入口、一套系統、一個 Bot**

| 指標 | 目前 | 目標 |
|------|------|------|
| 啟動指令 | 2 個（start.py / start_platform.py） | 1 個 |
| TG Bot 程式碼 | 2 套 | 1 套（新版） |
| 資料持久化 | 無 | SQLite（所有 session/cost/audit） |
| 派工 → 完成 → 通知 | 部分 | 完整 E2E |
| 費用追蹤 | 無 | 每次 spawn 自動記錄 |

## 非目標

- 不遷移到 PostgreSQL（保持 SQLite for dev）
- 不整合 Multica Cloud API（獨立運作）
- 不重寫 Agent Runtime（保持 spawn 模式）

---

## 方案

### 整合策略：合併到 `start_platform.py`

```
┌────────────────────────────────────────────┐
│ python start_platform.py                    │
│                                            │
│  1. init_db() → SQLite                     │
│  2. EventBus.start()                       │
│  3. uvicorn(Backend API :33333)            │
│  4. Agent Daemon (5 agents ready)          │
│  5. Telegram Bot (新版 src/telegram/)       │
│  6. Scheduler                              │
│                                            │
│  EventBus 連接一切：                        │
│  agent.output → cost_tracker               │
│                → audit_logger              │
│                → TG notification           │
│                → WS push                   │
└────────────────────────────────────────────┘
```

### 遷移步驟（5 步）

| # | 動作 | 影響 |
|---|------|------|
| 1 | 刪除 `start.py`，`start_platform.py` 改名為 `start.py` | 統一入口 |
| 2 | 刪除 `src/my_team/telegram_adapter.py` | 移除舊 Bot |
| 3 | `start_platform.py` 的 TG Bot 改用 `src/telegram/bot.py` | 新版 11 指令 |
| 4 | `team.yaml` 加入 `api_port` 欄位 | 設定統一 |
| 5 | `start-team.sh` 改為 `python start.py` | 腳本對齊 |

### 整合後的資料流

```
User (TG) ──→ /assign "建立 API"
                │
                ▼
         src/telegram/handlers/commands.py
                │
                ▼ POST /api/issues
         src/backend/api/issues.py
                │
                ▼ emit TASK_CREATED + TASK_ASSIGNED
         EventBus
                │
                ├─▶ audit_logger (記錄)
                │
                ▼
         Agent Daemon → spawn kiro-cli
                │
                ▼ emit AGENT_OUTPUT
         EventBus
                │
                ├─▶ cost_tracker (記錄費用)
                ├─▶ audit_logger (記錄)
                ├─▶ notifications.py → TG 回覆
                └─▶ ws.py → Web Dashboard push
```

---

## 執行計畫

### Phase A：清理（1 天）

| 任務 | 產出 |
|------|------|
| 備份 `start.py` → `start_legacy.py` | 保底回滾 |
| `start_platform.py` → `start.py` | 統一入口 |
| 刪除 `src/my_team/telegram_adapter.py` | 清理舊碼 |
| 更新 `start-team.sh`：`python start.py` | 腳本對齊 |
| 更新 `.env.example`：加 `API_PORT=33333` | 文件 |

### Phase B：接線（2 天）

| 任務 | 產出 |
|------|------|
| `start.py` TG 區塊改用 `src/telegram/bot.py` 的 `create_bot()` | 新 Bot 啟動 |
| Agent output → 建立 `agent_sessions` 記錄 | Session 持久化 |
| Agent output → emit `AGENT_OUTPUT` → `cost_tracker` | 費用記錄 |
| TG `/assign` → `POST /api/issues` → assign → daemon.send | 完整派工鏈路 |
| TG `NotificationService` 接收 `TASK_COMPLETED` → 回覆 | 完整通知鏈路 |

### Phase C：驗證（1 天）

| 任務 | 驗收條件 |
|------|---------|
| `python start.py` 一鍵啟動全部 | 5 agents ready + API :33333 + TG Bot online |
| TG `/status` | 回傳 5 agents 狀態卡片 |
| TG `/assign 寫一個 hello` | 建 Issue → assign → agent 執行 → TG 收到結果 |
| TG `/costs` | 顯示剛才的 spawn 費用 |
| `curl /api/admin/audit` | 有完整操作記錄 |
| `curl /api/ws/events`（WebSocket） | 即時收到事件 |

### Phase D：文件收尾（半天）

| 任務 | 產出 |
|------|------|
| 更新 `README.md` | 移除雙入口說明 |
| 刪除 `start_legacy.py`（確認無問題後） | 清理 |
| 更新 `docs/plans/ark-platform-execution-plan.md` 標記完成 | 文件同步 |

---

## 時程

```
Day 1（上午）：Phase A 清理
Day 1（下午）：Phase B 接線前半（session + cost）
Day 2（上午）：Phase B 接線後半（TG 完整鏈路）
Day 2（下午）：Phase C 驗證
Day 3（上午）：Phase D 文件 + buffer
```

**總計：2.5 天**

---

## 風險

| 風險 | 緩解 |
|------|------|
| 刪舊 Bot 後 TG 斷線 | `start_legacy.py` 保留 1 週可回滾 |
| EventBus 事件沒到 | 加 debug log，每個 emit 點都有 trace |
| Agent 回覆太慢（>5 min） | timeout 300s + 超時自動通知 |

---

## 成功標準

```
✅ 單一指令 `python start.py` 啟動全平台
✅ TG 發「/assign 建立 API」→ 30 秒內收到「⏳ 處理中」→ 3 分鐘內收到結果
✅ /costs 顯示本次費用
✅ /api/admin/audit 有完整記錄鏈
✅ 無殘留舊程式碼（telegram_adapter.py 已刪）
```

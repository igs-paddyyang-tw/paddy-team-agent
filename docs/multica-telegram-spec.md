# Multica × Telegram — 互動與呈現執行計畫

> 日期：2026-06-17
> 目標：透過 Telegram Bot 操作 Multica 平台（派工、監控、互動），替代/補充 Web UI

---

## 核心概念

```
Telegram User ─── @multica_bot ─── Multica Go Backend ─── Agent Daemon
                                         │
                                    PostgreSQL
```

Telegram 作為 Multica 的**行動操作介面**：
- 派工（建 Issue、指派 Agent）
- 監控（即時狀態、費用警報）
- 互動（Agent 回報、Blocker 通知、審批）

---

## 一、Telegram Bot 功能清單

### 指令系統

| 指令 | 功能 | 呈現方式 |
|------|------|---------|
| `/start` | 歡迎 + Workspace 綁定 | InlineKeyboard 選擇 |
| `/status` | 團隊即時狀態 | 表格格式 |
| `/agents` | Agent 列表 + 狀態 | InlineKeyboard |
| `/assign <描述>` | 建立 Issue 並指派 | 自動路由到適合的 Agent |
| `/board` | 看板摘要（進行中/待處理） | 按狀態分類列表 |
| `/costs` | 今日/本週費用 | KPI 卡片格式 |
| `/queue` | 待處理佇列 | 帶優先級標記 |
| `/stop <agent>` | 中斷 Agent 執行 | 確認 InlineKeyboard |
| `/retry <issue_id>` | 重試失敗任務 | 直接執行 |
| `/logs <agent>` | 最近執行日誌 | 截斷顯示 + 完整檔案 |
| `/settings` | Bot 設定 | InlineKeyboard 選單 |

### 自然語言互動

| 輸入 | 行為 |
|------|------|
| `@leader 規劃 Todo App` | 指定 agent 接收 |
| `規劃一個 API` | 自動路由到 leader |
| `查一下費用` | 觸發 `/costs` |
| `coder 做得怎樣了` | 查詢指定 agent 狀態 |

### 主動通知（Bot → User）

| 事件 | 通知內容 | 時機 |
|------|---------|------|
| 任務完成 | ✅ `coder-agent` 完成 #42「建立 API」 | 即時 |
| 任務失敗 | ❌ `qa-agent` 失敗 #38，原因：timeout | 即時 |
| Blocker | 🚫 `coder-agent` 回報阻塞：「需要 DB schema」 | 即時 |
| 預算警報 | ⚠️ 今日費用已達 80%（$24/$30） | 達閾值時 |
| 每日摘要 | 📊 今日完成 8 / 失敗 1 / 進行中 3 | 每日 21:00 |
| Agent 異常 | 🔴 `ai-dev-agent` 離線超過 5 分鐘 | 偵測到時 |

---

## 二、訊息呈現格式

### 狀態卡片

```
🤖 Agent Team Status
━━━━━━━━━━━━━━━━━━━
🧠 pm-agent      │ 🟢 idle
🤖 ai-dev-agent  │ 🔵 executing #42
💻 coder-agent   │ 🔵 executing #43
🧪 qa-agent      │ 🟢 idle
⚙️ admin-agent   │ 🟢 idle
━━━━━━━━━━━━━━━━━━━
📊 今日: 完成 5 │ 失敗 0 │ 進行中 2
💰 費用: $4.32 / $30.00
```

### 任務完成通知

```
✅ 任務完成

📋 #42 — 建立 Express.js REST API
🤖 coder-agent
⏱️ 耗時: 2 分 18 秒
💰 消耗: $0.45 (12,000 tokens)

📝 摘要:
已建立 Express.js API，包含：
• /api/users CRUD
• JWT 認證
• Swagger 文件

[查看詳情] [指派 QA 測試] [關閉]
```

### 看板摘要

```
📋 Board — My Workspace
━━━━━━━━━━━━━━━━━━━

🔵 進行中 (2)
├ #42 建立 REST API → coder-agent
└ #43 設計 RAG pipeline → ai-dev-agent

🟡 待處理 (3)
├ #44 撰寫單元測試 (P1)
├ #45 部署到 staging (P2)
└ #46 更新文件 (P3)

✅ 今日完成 (5)
└ #38 #39 #40 #41 #37

[指派待處理] [建立新任務] [重新整理]
```

### 費用報告

```
💰 Cost Report — 本週
━━━━━━━━━━━━━━━━━━━

今日: $4.32 │ 本週: $18.90
預算: $30/天 │ 使用: 14%

📊 按 Agent:
├ 💻 coder    $8.50 (45%)
├ 🤖 ai-dev   $5.30 (28%)
├ 🧪 qa       $3.20 (17%)
└ 🧠 pm       $1.90 (10%)

📈 趨勢: ↑12% vs 上週

[詳細報表] [設定預算]
```

### Blocker 通知（需互動）

```
🚫 Blocker 回報

🤖 coder-agent 執行 #42 時遇到阻塞：

「需要 PostgreSQL 的 schema 定義，
  目前 user_profiles 表結構未定義。
  請提供 schema 或授權我自行設計。」

[授權自行設計] [我來提供] [轉給 ai-dev]
```

---

## 三、InlineKeyboard 互動設計

### 任務指派流程

```
User: "建立一個登入頁面"

Bot: 📋 建立新任務
     「建立一個登入頁面」

     指派給誰？
     [🧠 pm-agent (規劃)] [💻 coder-agent (直接做)]
     [🤖 ai-dev-agent]    [自動判斷]

User: clicks [💻 coder-agent]

Bot: ✅ 已建立 Issue #47 並指派給 coder-agent
     ⏳ 開始執行...
```

### 審批流程（Agent 請求確認）

```
Bot: 🔔 coder-agent 請求確認

     「我準備刪除 legacy/ 目錄下的 15 個檔案，
      這些是舊版 API 程式碼。確認刪除？」

     [✅ 確認] [❌ 拒絕] [📝 修改指令]

User: clicks [✅ 確認]

Bot: ✅ 已授權，coder-agent 繼續執行...
```

### 多步驟進度更新

```
Bot: ⏳ coder-agent 執行 #42

     [■■■■■□□□□□] 50%

     ✅ 1/4 建立專案結構
     ✅ 2/4 實作 API 端點
     🔵 3/4 撰寫測試中...
     ⬜ 4/4 整合文件

     [中斷] [查看日誌]
```

---

## 四、Group Topics 模式

Multica 支援 Telegram Group（Forum Topics）讓團隊協作：

```
Multica Team (Group)
├── 📌 General          # 系統公告、狀態
├── 🧠 pm-agent         # Leader 的對話與派工記錄
├── 💻 coder-agent      # Coder 的執行回報
├── 🤖 ai-dev-agent     # AI Dev 的設計討論
├── 🧪 qa-agent         # QA 的測試結果
├── 📊 Daily Report     # 每日自動摘要
└── ⚠️ Alerts           # 預算/異常警報
```

每個 Agent 的回覆自動進入對應 Topic，人類可在任何 Topic @mention Agent。

---

## 五、技術實作

### 架構

```
┌──────────────────────┐
│ Telegram Bot API     │
│ (python-telegram-bot)│
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ TelegramAdapter      │
│ • 指令 handler       │
│ • 自然語言路由       │
│ • InlineKeyboard 管理│
│ • 通知推送           │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Multica Go Backend   │
│ /api/issues          │
│ /api/agents          │
│ /api/runs            │
│ WebSocket (events)   │
└──────────────────────┘
```

### 通知推送方式

```python
class NotificationService:
    """監聽 Multica WebSocket 事件 → 推送 Telegram。"""

    async def connect(self):
        async with websockets.connect(MULTICA_WS_URL) as ws:
            async for msg in ws:
                event = json.loads(msg)
                await self._dispatch(event)

    async def _dispatch(self, event):
        match event["type"]:
            case "task.completed":
                await self._notify_completed(event)
            case "task.failed":
                await self._notify_failed(event)
            case "agent.blocker":
                await self._notify_blocker(event)
            case "budget.warning":
                await self._notify_budget(event)
```

### API 呼叫（Bot → Multica Backend）

```python
class MulticaClient:
    """Multica API 客戶端。"""

    def __init__(self, base_url: str, api_key: str): ...

    async def create_issue(self, title: str, assignee: str = None) -> dict:
        return await self._post("/api/issues", {"title": title, "assignee": assignee})

    async def get_agents(self) -> list[dict]:
        return await self._get("/api/agents")

    async def get_board(self) -> dict:
        return await self._get("/api/issues?view=board")

    async def get_costs(self, range: str = "today") -> dict:
        return await self._get(f"/api/admin/costs?range={range}")

    async def abort_run(self, agent_id: str) -> bool:
        return await self._post(f"/api/agents/{agent_id}/abort", {})
```

---

## 六、執行計畫

### Phase 1：基礎骨架（Week 1）

| 天 | 任務 | 產出 |
|----|------|------|
| D1 | Telegram Bot 註冊 + 基礎 handler（/start, /status） | `src/telegram/bot.py` |
| D1 | MulticaClient（API 呼叫封裝） | `src/telegram/multica_client.py` |
| D2 | /agents, /board 指令 | 狀態查詢功能 |
| D2 | 訊息格式化（表格、卡片） | `src/telegram/formatters.py` |
| D3 | /assign 指派流程 + InlineKeyboard | 任務建立完整流程 |

### Phase 2：互動與通知（Week 2）

| 天 | 任務 | 產出 |
|----|------|------|
| D4 | WebSocket 事件監聽 + 通知推送 | `src/telegram/notifications.py` |
| D4 | 任務完成/失敗/blocker 通知 | 即時事件推送 |
| D5 | 自然語言路由（@mention + 關鍵字） | 智能路由 |
| D5 | /costs 費用報告 + 預算警報 | 費用功能 |
| D6 | InlineKeyboard callback 處理（審批、確認） | 互動流程 |

### Phase 3：進階功能（Week 3）

| 天 | 任務 | 產出 |
|----|------|------|
| D7 | Group Topics 模式（多 Topic 路由） | 群組支援 |
| D7 | 進度更新（edit_message 即時刷新） | 進度條 |
| D8 | /logs, /retry, /stop 操作指令 | 管理功能 |
| D8 | 每日摘要排程（21:00 自動推送） | 定時報告 |
| D9 | 權限控制（admin/member 分級） | 安全性 |
| D9 | 多 Workspace 支援 | 切換 workspace |

---

## 七、與現有 my-team 的整合路徑

目前 `my-team` 的 TelegramAdapter 已能：
- ✅ 收發訊息
- ✅ @mention 路由
- ✅ Agent spawn + 回覆

要對接 Multica Backend 需改為：
1. `daemon.send_to()` → `multica_client.create_issue()` + assign
2. Agent output → Multica event stream → 通知
3. 本地 kiro-cli spawn → Multica Runtime 執行

```diff
- await daemon.send_to("pm-agent", text)      # 直接 spawn kiro-cli
+ issue = await multica.create_issue(text)     # 建立 Issue
+ await multica.assign(issue.id, "pm-agent")   # 指派 → Runtime 執行
```

這樣就能同時在 Telegram 和 Multica Web UI 看到相同的任務狀態。

---
title: "Ark Telegram UI/UX"
status: implemented
type: spec
author: paddyyang
created: 2026-06-17
---

# Ark Telegram UI/UX

Telegram Bot 的 UI/UX 層規格書 — 訊息格式化、InlineKeyboard、進度更新、通知推送。
對應 Multica 平台的行動操作介面。

---

## 1. 問題陳述

現有 `TelegramAdapter`（`src/bot/handlers.py`）僅支援純文字收發，存在以下限制：

| 缺失能力 | 影響 |
|----------|------|
| Rich UI（InlineKeyboard / 卡片格式） | 使用者無法一鍵操作，需記憶指令語法 |
| 主動通知推送 | 任務完成、異常告警只能使用者主動查詢 |
| Group Topics 路由 | 多 Agent 訊息混雜，無法按職責分流 |
| 多 Workspace 支援 | 一個 Bot 只能綁定一個工作空間 |
| 進度即時更新 | 長任務（>5s）使用者無回饋，不知是否卡住 |
| 訊息格式引擎 | 每個 handler 各自拼字串，風格不一致 |

### 現有架構瓶頸

```python
# 現狀：handlers.py 中的典型回覆
await msg.reply_text(f"任務完成：{result}")  # 純文字，無格式，無互動
```

使用者痛點：
- 審批流程需要多次來回對話（「確認嗎？」→「是」→「哪個？」→「第二個」）
- 費用報告、看板摘要等結構化資訊以純文字呈現，閱讀困難
- 群組中多個 Agent 的訊息混在一起，無法快速定位

---

## 2. 目標與非目標

### 目標

| # | 目標 | 衡量指標 |
|---|------|---------|
| G1 | 11 個 slash 指令覆蓋核心操作 | 所有指令回應 < 2s |
| G2 | 6 種主動通知（任務/費用/異常/日報/審批/提醒） | 事件觸發 → 推送延遲 < 5s |
| G3 | InlineKeyboard 互動流程（指派/審批/確認） | 操作步驟減少 60% |
| G4 | Group Topics 模式（每 Agent 一個 Topic） | 訊息正確路由率 100% |
| G5 | 訊息格式化引擎（5 種卡片模板） | UI 風格一致性 |
| G6 | 進度即時更新（edit_message） | 長任務有視覺回饋 |
| G7 | 多 Workspace 綁定 | 單 Bot 支援 ≥5 個 Workspace |

### 非目標

- ❌ Web UI Dashboard（由 `ark-frontend-design` 負責）
- ❌ Mobile App（原生 iOS/Android）
- ❌ 語音訊息處理（STT/TTS）
- ❌ Telegram Payment API 整合
- ❌ Telegram Mini App（WebApp）
- ❌ 檔案上傳/下載管理（由 `telegram_send_file` Skill 負責）

---

## 3. 核心設計

### 3.1 模組結構

```
src/telegram/
├── __init__.py
├── bot.py                  # Application 入口 + handler 註冊
├── config.py               # TG Bot 設定（token / webhook / topics mapping）
├── handlers/
│   ├── __init__.py
│   ├── commands.py         # 11 個 slash 指令 handler
│   ├── messages.py         # 自然語言路由（意圖分類 → Skill 分派）
│   └── callbacks.py        # InlineKeyboard callback_data 路由
├── formatters.py           # 訊息格式化引擎（5 種卡片模板）
├── keyboards.py            # InlineKeyboard 工廠（3 種互動流程）
├── notifications.py        # WebSocket 事件監聽 → TG 推送
└── progress.py             # edit_message_text 進度更新器
```

### 3.2 指令清單（11 個 Slash Commands）

| # | 指令 | 功能 | 回應格式 |
|---|------|------|---------|
| 1 | `/start` | 綁定 Workspace + 歡迎 | 文字 + InlineKeyboard（選擇 Workspace） |
| 2 | `/status` | 查詢當前衝刺狀態 | Status Card |
| 3 | `/board` | 看板摘要（Todo/Doing/Done） | Board Card |
| 4 | `/assign <task>` | 指派任務給 Agent | InlineKeyboard（選擇 Agent） |
| 5 | `/cost` | 本月 LLM 費用摘要 | Cost Card |
| 6 | `/approve` | 待審批項目列表 | InlineKeyboard（批准/拒絕） |
| 7 | `/notify <on/off>` | 通知偏好設定 | InlineKeyboard（勾選通知類型） |
| 8 | `/workspace` | 切換 Workspace | InlineKeyboard（Workspace 列表） |
| 9 | `/blockers` | 列出阻塞項目 | Blocker Card |
| 10 | `/daily` | 觸發每日站報 | Completed Card |
| 11 | `/help` | 指令說明 | 格式化文字 |


### 3.3 訊息格式規範（5 種卡片模板）

所有卡片使用 Telegram MarkdownV2 格式，由 `formatters.py` 統一產出。

#### Template 1: Status Card（衝刺狀態）

```
📊 *Sprint 2026\-W25 狀態*

▸ 進度：████████░░ 78%
▸ 剩餘天數：3 天
▸ 待辦：4 ┃ 進行中：6 ┃ 完成：12

⚡ *活躍 Agents*
• 🏗️ Architect — 設計 API schema
• 💻 Coder — 實作 payment module
• 🧪 Tester — E2E 測試執行中

🚨 *阻塞* ：2 項需要注意
```

#### Template 2: Completed Card（完成摘要）

```
✅ *每日完成摘要* — 2026\-06\-17

┌─────────────────────────────┐
│ 🏗️ Architect                │
│   ✓ API schema v2 定稿      │
│   ✓ DB migration 設計       │
├─────────────────────────────┤
│ 💻 Coder                    │
│   ✓ payment module 80%     │
│   ✓ unit tests \+12         │
├─────────────────────────────┤
│ 🧪 Tester                   │
│   ✓ E2E 5/8 passed         │
│   ⚠️ 3 flaky tests          │
└─────────────────────────────┘

📈 *產出統計*：PR \+5 ┃ Commits \+23 ┃ Tests \+12
```

#### Template 3: Board Card（看板摘要）

```
📋 *看板摘要*

*📌 Todo \(4\)*
  1\. 整合第三方支付
  2\. 效能壓測
  3\. 文件更新
  4\. 部署腳本

*🔄 In Progress \(3\)*
  1\. Payment module — 💻 Coder \(80%\)
  2\. E2E tests — 🧪 Tester \(62%\)
  3\. API docs — 🏗️ Architect \(90%\)

*✅ Done \(12\)*
  最近：DB migration、Auth flow、CI pipeline
```

#### Template 4: Cost Card（費用報告）

```
💰 *LLM 費用報告* — 2026年6月

┌──────────────┬─────────┬─────────┐
│ Agent        │ Tokens  │ Cost    │
├──────────────┼─────────┼─────────┤
│ 🏗️ Architect │ 245K    │ $1\.23  │
│ 💻 Coder     │ 1\.2M   │ $6\.40  │
│ 🧪 Tester    │ 89K     │ $0\.45  │
│ 📝 Writer    │ 156K    │ $0\.78  │
├──────────────┼─────────┼─────────┤
│ *合計*       │ *1\.69M*│ *$8\.86*│
└──────────────┴─────────┴─────────┘

📊 vs 上月：\+12% ┃ 預算剩餘：$41\.14
⚠️ Coder 用量偏高，建議檢查 prompt 效率
```

#### Template 5: Blocker Card（阻塞項目）

```
🚨 *阻塞項目* — 需要處理

1️⃣ *第三方 API 回應逾時*
   ▸ 影響：Payment module 無法整合測試
   ▸ 負責：💻 Coder
   ▸ 等待：廠商技術支援回覆
   ▸ 已阻塞：2 天

2️⃣ *測試環境 DB 滿載*
   ▸ 影響：E2E 測試無法執行
   ▸ 負責：🧪 Tester
   ▸ 需要：DevOps 擴容
   ▸ 已阻塞：1 天

💡 建議動作：[處理阻塞] [跳過] [升級]
```

#### Formatter 實作

```python
# src/telegram/formatters.py
from dataclasses import dataclass
from enum import Enum

class CardType(Enum):
    STATUS = "status"
    COMPLETED = "completed"
    BOARD = "board"
    COST = "cost"
    BLOCKER = "blocker"

@dataclass
class CardData:
    card_type: CardType
    title: str
    payload: dict

class TelegramFormatter:
    """統一訊息格式化引擎。"""

    def format(self, data: CardData) -> str:
        """根據 card_type 分派到對應模板。"""
        renderer = getattr(self, f"_render_{data.card_type.value}", None)
        if not renderer:
            return str(data.payload)
        return renderer(data.title, data.payload)

    def _render_status(self, title: str, payload: dict) -> str:
        progress = payload["progress"]
        bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        agents = "\n".join(
            f"• {a['icon']} {a['name']} — {a['task']}"
            for a in payload["agents"]
        )
        return (
            f"📊 *{self._escape(title)}*\n\n"
            f"▸ 進度：{bar} {progress}%\n"
            f"▸ 剩餘天數：{payload['days_left']} 天\n"
            f"▸ 待辦：{payload['todo']} ┃ 進行中：{payload['doing']} ┃ 完成：{payload['done']}\n\n"
            f"⚡ *活躍 Agents*\n{agents}"
        )

    def _render_cost(self, title: str, payload: dict) -> str:
        rows = "\n".join(
            f"│ {a['icon']} {a['name']:<10} │ {a['tokens']:<7} │ ${a['cost']:<5.2f} │"
            for a in payload["agents"]
        )
        total = sum(a["cost"] for a in payload["agents"])
        return (
            f"💰 *{self._escape(title)}*\n\n"
            f"┌──────────────┬─────────┬─────────┐\n"
            f"│ Agent        │ Tokens  │ Cost    │\n"
            f"├──────────────┼─────────┼─────────┤\n"
            f"{rows}\n"
            f"├──────────────┼─────────┼─────────┤\n"
            f"│ *合計*       │         │ *${total:.2f}* │\n"
            f"└──────────────┴─────────┴─────────┘"
        )

    @staticmethod
    def _escape(text: str) -> str:
        """Escape MarkdownV2 特殊字元。"""
        special = r"_*[]()~`>#+-=|{}.!"
        for ch in special:
            text = text.replace(ch, f"\\{ch}")
        return text
```


### 3.4 InlineKeyboard 互動流程

三種核心互動 flow，由 `keyboards.py` 產生按鈕，`callbacks.py` 處理回調。

#### Flow 1: 指派流程（Assign）

```
使用者: /assign 整合第三方支付 API
  ↓
Bot: 選擇負責 Agent
  [🏗️ Architect] [💻 Coder] [🧪 Tester] [📝 Writer]
  ↓ 使用者點擊 [💻 Coder]
Bot: 設定優先級
  [🔴 High] [🟡 Medium] [🟢 Low]
  ↓ 使用者點擊 [🔴 High]
Bot: ✅ 已指派給 💻 Coder（優先級：High）
     任務：整合第三方支付 API
     [撤銷] [查看看板]
```

#### Flow 2: 審批流程（Approve）

```
Bot（主動通知）: 📋 待審批項目
  ↓
  1. PR #142: payment module — 💻 Coder
     [✅ 批准] [❌ 拒絕] [💬 留言]
  2. Deploy request: staging — 🏗️ Architect
     [✅ 批准] [❌ 拒絕] [💬 留言]
  ↓ 使用者點擊 [✅ 批准] on PR #142
Bot: ✅ PR #142 已批准
     自動觸發 merge + deploy pipeline
```

#### Flow 3: 確認流程（Confirm）

```
Bot: ⚠️ 即將執行破壞性操作
     動作：重置 staging 環境
     影響：所有測試資料將被清除
  [確認執行] [取消]
  ↓ 使用者點擊 [確認執行]
Bot: ⏳ 正在執行... (progress update)
Bot: ✅ staging 環境已重置（耗時 45s）
```

#### Keyboard 工廠實作

```python
# src/telegram/keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class KeyboardFactory:
    """InlineKeyboard 按鈕工廠。"""

    # callback_data 格式: {flow}:{action}:{entity_id}:{extra}
    # 例: assign:select_agent:task_123:coder

    @staticmethod
    def agent_selector(task_id: str, agents: list[dict]) -> InlineKeyboardMarkup:
        """產生 Agent 選擇鍵盤。"""
        buttons = [
            InlineKeyboardButton(
                text=f"{a['icon']} {a['name']}",
                callback_data=f"assign:select_agent:{task_id}:{a['id']}",
            )
            for a in agents
        ]
        # 每行最多 3 個按鈕
        rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def priority_selector(task_id: str, agent_id: str) -> InlineKeyboardMarkup:
        """產生優先級選擇鍵盤。"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🔴 High", callback_data=f"assign:priority:{task_id}:high"),
            InlineKeyboardButton("🟡 Medium", callback_data=f"assign:priority:{task_id}:medium"),
            InlineKeyboardButton("🟢 Low", callback_data=f"assign:priority:{task_id}:low"),
        ]])

    @staticmethod
    def approval_buttons(item_id: str, item_type: str) -> InlineKeyboardMarkup:
        """產生審批按鈕。"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ 批准", callback_data=f"approve:accept:{item_id}:{item_type}"),
            InlineKeyboardButton("❌ 拒絕", callback_data=f"approve:reject:{item_id}:{item_type}"),
            InlineKeyboardButton("💬 留言", callback_data=f"approve:comment:{item_id}:{item_type}"),
        ]])

    @staticmethod
    def confirm_action(action_id: str) -> InlineKeyboardMarkup:
        """產生確認/取消按鈕。"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ 確認執行", callback_data=f"confirm:yes:{action_id}:"),
            InlineKeyboardButton("❌ 取消", callback_data=f"confirm:no:{action_id}:"),
        ]])

    @staticmethod
    def workspace_selector(workspaces: list[dict]) -> InlineKeyboardMarkup:
        """產生 Workspace 選擇鍵盤。"""
        buttons = [
            [InlineKeyboardButton(
                text=f"{'✅ ' if ws['active'] else ''}{ws['name']}",
                callback_data=f"workspace:switch:{ws['id']}:",
            )]
            for ws in workspaces
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def notification_settings(current: dict) -> InlineKeyboardMarkup:
        """產生通知偏好設定鍵盤（toggle 模式）。"""
        types = [
            ("task_complete", "✅ 任務完成"),
            ("cost_alert", "💰 費用警告"),
            ("blocker", "🚨 阻塞通知"),
            ("daily_report", "📊 每日報表"),
            ("approval", "📋 審批請求"),
            ("mention", "💬 被提及"),
        ]
        buttons = [
            [InlineKeyboardButton(
                text=f"{'🟢' if current.get(t[0], True) else '🔴'} {t[1]}",
                callback_data=f"notify:toggle:{t[0]}:",
            )]
            for t in types
        ]
        buttons.append([InlineKeyboardButton("💾 儲存", callback_data="notify:save::")])
        return InlineKeyboardMarkup(buttons)
```

#### Callback 路由

```python
# src/telegram/handlers/callbacks.py
from telegram import Update
from telegram.ext import ContextTypes

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """統一 callback_data 路由器。"""
    query = update.callback_query
    await query.answer()  # 停止 loading 動畫

    # 解析 callback_data: {flow}:{action}:{entity_id}:{extra}
    parts = query.data.split(":")
    if len(parts) < 4:
        return
    flow, action, entity_id, extra = parts[0], parts[1], parts[2], parts[3]

    router = {
        "assign": _handle_assign_callback,
        "approve": _handle_approve_callback,
        "confirm": _handle_confirm_callback,
        "workspace": _handle_workspace_callback,
        "notify": _handle_notify_callback,
    }

    handler = router.get(flow)
    if handler:
        await handler(query, action, entity_id, extra, context)
```

### 3.5 Group Topics 路由

Telegram Supergroup 的 Forum Topics 功能，每個 Agent 擁有獨立 Topic：

```
Multica Team Group (Supergroup with Topics enabled)
├── 📌 General          → 人類成員討論 + Bot 全域通知
├── 🏗️ Architect        → 架構設計相關訊息
├── 💻 Coder            → 程式碼實作相關訊息
├── 🧪 Tester           → 測試報告與結果
├── 📝 Writer           → 文件產出
├── 📊 Daily Reports    → 自動日報匯總
└── 🚨 Alerts           → 阻塞 + 費用警告 + 異常
```

#### Topics 路由規則

```python
# src/telegram/config.py
from dataclasses import dataclass

@dataclass
class TopicRouting:
    """Group Topics 路由設定。"""

    # Agent ID → Topic ID 映射（由 /start 設定時建立）
    agent_topics: dict[str, int]  # {"architect": 12345, "coder": 12346, ...}

    # 特殊 Topics
    general_topic: int = 0          # General（預設，topic_id=0 或 None）
    daily_topic: int = 0            # Daily Reports
    alert_topic: int = 0            # Alerts

    def get_topic_for_agent(self, agent_id: str) -> int | None:
        """取得 Agent 對應的 Topic ID。"""
        return self.agent_topics.get(agent_id)

    def get_topic_for_event(self, event_type: str) -> int | None:
        """取得事件類型對應的 Topic ID。"""
        routing = {
            "task_complete": None,       # → Agent's own topic
            "daily_report": self.daily_topic,
            "cost_alert": self.alert_topic,
            "blocker": self.alert_topic,
            "approval": self.general_topic,
            "mention": self.general_topic,
        }
        return routing.get(event_type, self.general_topic)
```

#### 訊息發送時的 Topic 路由

```python
# src/telegram/notifications.py（部分）
async def send_to_topic(
    bot: Bot,
    chat_id: int,
    message_thread_id: int | None,
    text: str,
    parse_mode: str = "MarkdownV2",
    reply_markup=None,
) -> None:
    """發送訊息到指定 Topic。"""
    await bot.send_message(
        chat_id=chat_id,
        message_thread_id=message_thread_id,
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )
```


### 3.6 進度即時更新

長任務（預估 >3s）使用 `edit_message_text` 即時更新進度：

```python
# src/telegram/progress.py
import asyncio
from telegram import Bot, Message

class ProgressUpdater:
    """透過 edit_message_text 即時更新任務進度。"""

    THROTTLE_MS = 800  # Telegram API 節流（避免 429 Too Many Requests）

    def __init__(self, bot: Bot, chat_id: int, message_id: int):
        self._bot = bot
        self._chat_id = chat_id
        self._message_id = message_id
        self._last_update = 0.0
        self._current_text = ""

    async def start(self, task_name: str) -> None:
        """發送初始進度訊息。"""
        self._current_text = f"⏳ *{task_name}*\n\n▸ 準備中..."
        msg = await self._bot.send_message(
            chat_id=self._chat_id,
            text=self._current_text,
            parse_mode="MarkdownV2",
        )
        self._message_id = msg.message_id

    async def update(self, step: int, total: int, description: str) -> None:
        """更新進度（含節流）。"""
        now = asyncio.get_event_loop().time()
        if (now - self._last_update) * 1000 < self.THROTTLE_MS:
            return

        pct = int(step / total * 100)
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        text = f"⏳ 執行中\n\n{bar} {pct}%\n▸ {description}\n▸ 步驟 {step}/{total}"

        if text != self._current_text:
            await self._bot.edit_message_text(
                chat_id=self._chat_id,
                message_id=self._message_id,
                text=text,
                parse_mode="MarkdownV2",
            )
            self._current_text = text
            self._last_update = now

    async def complete(self, result_text: str) -> None:
        """標記完成，替換為結果卡片。"""
        await self._bot.edit_message_text(
            chat_id=self._chat_id,
            message_id=self._message_id,
            text=result_text,
            parse_mode="MarkdownV2",
        )
```

---

## 4. API 依賴

本模組需要 Multica Backend 提供以下 API 端點：

### 4.1 核心 API

| 方法 | 端點 | 用途 | 回傳 |
|------|------|------|------|
| GET | `/api/v1/workspaces` | 列出使用者的 Workspace | `[{id, name, role}]` |
| GET | `/api/v1/workspaces/{id}/sprint` | 當前衝刺狀態 | `{progress, days_left, counts}` |
| GET | `/api/v1/workspaces/{id}/board` | 看板資料 | `{todo, doing, done}` |
| GET | `/api/v1/workspaces/{id}/agents` | Agent 列表 | `[{id, name, icon, status}]` |
| POST | `/api/v1/tasks` | 建立任務 | `{task_id, status}` |
| PATCH | `/api/v1/tasks/{id}/assign` | 指派任務 | `{ok}` |
| GET | `/api/v1/approvals/pending` | 待審批列表 | `[{id, type, title, author}]` |
| POST | `/api/v1/approvals/{id}/decide` | 審批決定 | `{ok}` |
| GET | `/api/v1/costs/summary` | 費用摘要 | `{agents, total, budget}` |
| GET | `/api/v1/blockers` | 阻塞列表 | `[{id, title, agent, days}]` |
| GET | `/api/v1/daily-report` | 每日完成摘要 | `{agents, stats}` |

### 4.2 WebSocket 事件（通知推送用）

| 事件 | Payload | 觸發通知 |
|------|---------|---------|
| `task.completed` | `{task_id, agent, title}` | ✅ 任務完成通知 |
| `cost.threshold` | `{agent, current, limit}` | 💰 費用警告 |
| `blocker.created` | `{blocker_id, title, agent}` | 🚨 新阻塞 |
| `daily.ready` | `{date, summary}` | 📊 每日報表就緒 |
| `approval.requested` | `{item_id, type, author}` | 📋 審批請求 |
| `agent.mention` | `{from, message, context}` | 💬 被提及 |

### 4.3 通知推送實作

```python
# src/telegram/notifications.py
import asyncio
import websockets
import json
from telegram import Bot

class NotificationListener:
    """監聽 Multica WebSocket 事件，推送到 Telegram。"""

    def __init__(self, bot: Bot, ws_url: str, formatter, routing: TopicRouting):
        self._bot = bot
        self._ws_url = ws_url
        self._formatter = formatter
        self._routing = routing
        self._subscribers: dict[str, list[int]] = {}  # event_type → [chat_ids]

    async def start(self) -> None:
        """啟動 WebSocket 監聽（含自動重連）。"""
        while True:
            try:
                async with websockets.connect(self._ws_url) as ws:
                    async for raw in ws:
                        event = json.loads(raw)
                        await self._dispatch(event)
            except websockets.ConnectionClosed:
                await asyncio.sleep(5)  # 重連等待

    async def _dispatch(self, event: dict) -> None:
        """分派事件到訂閱者。"""
        event_type = event.get("type", "")
        payload = event.get("payload", {})

        # 查找訂閱者
        subscribers = self._subscribers.get(event_type, [])
        if not subscribers:
            return

        # 格式化訊息
        card = self._format_notification(event_type, payload)

        # 決定 Topic
        topic_id = self._routing.get_topic_for_event(event_type)
        if event_type == "task.completed":
            agent_id = payload.get("agent")
            topic_id = self._routing.get_topic_for_agent(agent_id) or topic_id

        # 推送
        for chat_id in subscribers:
            await send_to_topic(self._bot, chat_id, topic_id, card)

    def _format_notification(self, event_type: str, payload: dict) -> str:
        """將事件格式化為通知訊息。"""
        templates = {
            "task.completed": "✅ *任務完成*\n\n▸ {title}\n▸ Agent：{agent}",
            "cost.threshold": "💰 *費用警告*\n\n▸ {agent} 已使用 ${current:.2f}\n▸ 預算上限：${limit:.2f}",
            "blocker.created": "🚨 *新阻塞*\n\n▸ {title}\n▸ 負責：{agent}",
            "daily.ready": "📊 *每日報表就緒*\n\n▸ 日期：{date}",
            "approval.requested": "📋 *新審批請求*\n\n▸ {type}：{title}\n▸ 提交者：{author}",
            "agent.mention": "💬 *被提及*\n\n▸ {from}：{message}",
        }
        template = templates.get(event_type, str(payload))
        return template.format(**payload)
```

---

## 5. 資料模型

### 5.1 TG User → Workspace 綁定

```python
# src/telegram/models.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TelegramBinding:
    """Telegram 使用者與 Workspace 的綁定關係。"""
    telegram_user_id: int
    telegram_username: str
    workspace_id: str
    workspace_name: str
    active: bool = True
    role: str = "member"            # admin / member / viewer
    bound_at: datetime = field(default_factory=datetime.now)

@dataclass
class NotificationPreference:
    """通知偏好設定（per user per workspace）。"""
    telegram_user_id: int
    workspace_id: str
    task_complete: bool = True
    cost_alert: bool = True
    blocker: bool = True
    daily_report: bool = True
    approval: bool = True
    mention: bool = True
    quiet_hours_start: int | None = None   # 0-23，靜音開始
    quiet_hours_end: int | None = None     # 0-23，靜音結束

@dataclass
class GroupTopicConfig:
    """群組 Topics 設定。"""
    group_chat_id: int
    workspace_id: str
    agent_topics: dict[str, int] = field(default_factory=dict)
    daily_topic_id: int = 0
    alert_topic_id: int = 0
    general_topic_id: int = 0
    created_at: datetime = field(default_factory=datetime.now)
```

### 5.2 持久化

使用 SQLite（與既有 `data/sessions.db` 共用）：

```sql
-- Telegram 綁定表
CREATE TABLE IF NOT EXISTS telegram_bindings (
    telegram_user_id INTEGER NOT NULL,
    workspace_id TEXT NOT NULL,
    workspace_name TEXT NOT NULL,
    telegram_username TEXT DEFAULT '',
    active INTEGER DEFAULT 1,
    role TEXT DEFAULT 'member',
    bound_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (telegram_user_id, workspace_id)
);

-- 通知偏好表
CREATE TABLE IF NOT EXISTS notification_preferences (
    telegram_user_id INTEGER NOT NULL,
    workspace_id TEXT NOT NULL,
    task_complete INTEGER DEFAULT 1,
    cost_alert INTEGER DEFAULT 1,
    blocker INTEGER DEFAULT 1,
    daily_report INTEGER DEFAULT 1,
    approval INTEGER DEFAULT 1,
    mention INTEGER DEFAULT 1,
    quiet_hours_start INTEGER,
    quiet_hours_end INTEGER,
    PRIMARY KEY (telegram_user_id, workspace_id)
);

-- 群組 Topics 設定表
CREATE TABLE IF NOT EXISTS group_topic_configs (
    group_chat_id INTEGER NOT NULL,
    workspace_id TEXT NOT NULL,
    agent_topics TEXT DEFAULT '{}',  -- JSON
    daily_topic_id INTEGER DEFAULT 0,
    alert_topic_id INTEGER DEFAULT 0,
    general_topic_id INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_chat_id, workspace_id)
);
```


---

## 6. 非功能性需求

| NFR | 指標 | 衡量方式 |
|-----|------|---------|
| 回應延遲 | Slash 指令回應 < 2s（p95） | Bot 收到 update → 回覆 send 的時間差 |
| 通知延遲 | WebSocket 事件 → TG 推送 < 5s | 事件 timestamp → 訊息送達 timestamp |
| 並發能力 | 支援 100 concurrent users | 壓力測試：100 users × 10 msg/min |
| 可用性 | 99.5% uptime（月） | 健康檢查 + 自動重啟 |
| 節流保護 | 遵守 Telegram Bot API 速率限制 | 30 msg/s per chat，20 msg/min per user |
| 訊息大小 | 單訊息 ≤ 4096 字元 | 超長內容自動分段 |
| 記憶體 | Bot 進程 < 256MB | Docker resource limit |
| 啟動時間 | Cold start < 5s | 進程啟動 → 第一個 update 處理 |
| 錯誤恢復 | WebSocket 斷線自動重連 | 指數退避重試（5s → 10s → 30s → 60s） |
| 安全 | callback_data 防偽造 | HMAC 簽名驗證 |

### 速率限制策略

```python
# Telegram Bot API 限制
RATE_LIMITS = {
    "per_second_global": 30,        # 全域每秒最多 30 訊息
    "per_second_per_chat": 1,       # 同一 chat 每秒最多 1 訊息
    "per_minute_per_group": 20,     # 群組每分鐘最多 20 訊息
    "bulk_notification_delay": 0.05, # 批次通知間隔 50ms
}
```

### 長訊息分段

```python
MAX_MESSAGE_LENGTH = 4096

def split_message(text: str) -> list[str]:
    """超長訊息分段（優先在換行處切割）。"""
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]
    parts = []
    while text:
        if len(text) <= MAX_MESSAGE_LENGTH:
            parts.append(text)
            break
        # 找最後一個換行符
        cut = text[:MAX_MESSAGE_LENGTH].rfind("\n")
        if cut < MAX_MESSAGE_LENGTH // 2:
            cut = MAX_MESSAGE_LENGTH
        parts.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return parts
```

---

## 7. 驗收條件

### 7.1 Slash 指令驗收

| 指令 | Pass 條件 | Fail 條件 |
|------|----------|----------|
| `/start` | 顯示 Workspace 選擇鍵盤；選擇後綁定成功 | 無回應；綁定失敗無錯誤提示 |
| `/status` | 2s 內回傳 Status Card；數據正確 | 超時；數據與 API 不符 |
| `/board` | 顯示 Todo/Doing/Done 三欄；任務數正確 | 任務遺漏；格式錯亂 |
| `/assign <task>` | 顯示 Agent 選擇 → 優先級選擇 → 確認 | 流程中斷；任務未建立 |
| `/cost` | 顯示 Cost Card；金額與 API 一致 | 金額錯誤；Agent 遺漏 |
| `/approve` | 列出所有待審批項目；點擊後狀態更新 | 項目遺漏；審批無效 |
| `/notify` | 顯示當前設定（🟢/🔴）；toggle 後持久化 | 設定未保存；重啟後遺失 |
| `/workspace` | 列出綁定的 Workspace；切換後影響後續指令 | 切換無效；狀態不一致 |
| `/blockers` | 顯示 Blocker Card；阻塞天數正確 | 阻塞遺漏；天數計算錯誤 |
| `/daily` | 觸發並顯示 Completed Card | 無回應；資料為空 |
| `/help` | 列出所有指令及說明 | 指令遺漏；說明錯誤 |

### 7.2 通知推送驗收

| 事件 | Pass 條件 | Fail 條件 |
|------|----------|----------|
| `task.completed` | 5s 內推送到 Agent 對應 Topic | 超時；推送到錯誤 Topic |
| `cost.threshold` | 推送到 Alerts Topic；金額正確 | 未推送；金額錯誤 |
| `blocker.created` | 推送到 Alerts Topic；含負責 Agent | 未推送；資訊不完整 |
| `daily.ready` | 推送到 Daily Reports Topic | 未推送；格式錯亂 |
| `approval.requested` | 推送到 General；含審批按鈕 | 無按鈕；點擊無效 |
| `agent.mention` | 推送到被提及者私訊 | 未推送；錯誤對象 |

### 7.3 互動流程驗收

| Flow | Pass 條件 | Fail 條件 |
|------|----------|----------|
| 指派 | 3 步完成（Agent → Priority → 確認） | 步驟卡住；callback 無回應 |
| 審批 | 點擊後狀態即時更新；觸發後續動作 | 狀態未更新；重複觸發 |
| 確認 | 確認後執行；取消後清理 | 確認無效；取消仍執行 |

### 7.4 Group Topics 驗收

| 場景 | Pass 條件 | Fail 條件 |
|------|----------|----------|
| Agent 完成任務 | 通知出現在 Agent 對應 Topic | 出現在 General 或其他 Topic |
| 費用警告 | 出現在 Alerts Topic | 出現在 Agent Topic |
| 每日報表 | 出現在 Daily Reports Topic | 出現在多個 Topics |
| 人類指令 | 回應出現在同一 Topic（reply 模式） | 回應出現在 General |

---

## 8. 執行計畫

### 8.1 里程碑概覽（3 週 9 個工作天）

```
Week 1: 基礎建設
├── Day 1-2: 模組骨架 + 資料模型 + DB schema
├── Day 2-3: formatters.py（5 種卡片模板）+ keyboards.py
└── Day 3:   progress.py + 單元測試

Week 2: 指令 + 互動
├── Day 4-5: 11 個 slash 指令 handler + API 串接
├── Day 5-6: InlineKeyboard 3 種互動流程
└── Day 6:   callback 路由 + 狀態管理

Week 3: 通知 + Topics + 整合
├── Day 7:   WebSocket 監聽 + 6 種通知推送
├── Day 8:   Group Topics 路由 + 多 Workspace
└── Day 9:   整合測試 + 效能調校 + 文件
```

### 8.2 詳細任務

| Day | 任務 | 產出 | 驗證 |
|-----|------|------|------|
| D1 | 建立 `src/telegram/` 模組結構 | 7 個檔案骨架 | import 無錯誤 |
| D1 | 設計 DB schema + migration | 3 張表 | SQLite 建表成功 |
| D2 | 實作 `formatters.py` 5 種模板 | 格式化引擎 | 單元測試通過 |
| D2 | 實作 `keyboards.py` 按鈕工廠 | 5 種鍵盤 | snapshot 測試 |
| D3 | 實作 `progress.py` 進度更新 | 進度器 | mock 測試通過 |
| D4 | 實作 `/start` `/help` `/status` `/board` | 4 個指令 | 本地 Bot 手動測試 |
| D5 | 實作 `/assign` `/cost` `/approve` `/blockers` | 4 個指令 | API mock 測試 |
| D5 | 實作 `/notify` `/workspace` `/daily` | 3 個指令 | 本地 Bot 手動測試 |
| D6 | 實作 `callbacks.py` 3 種互動流程 | callback 路由 | E2E flow 測試 |
| D7 | 實作 `notifications.py` WebSocket 監聽 | 通知推送 | mock WS 測試 |
| D8 | 實作 Group Topics 路由 | Topics 分流 | 群組實際測試 |
| D8 | 多 Workspace 綁定 + 切換 | Workspace 管理 | 切換驗證 |
| D9 | 整合測試 + 效能測試 | 測試報告 | 所有驗收條件通過 |
| D9 | README + 設定文件 | 文件 | 新人可依文件啟動 |

### 8.3 風險與緩解

| 風險 | 影響 | 機率 | 緩解 |
|------|------|------|------|
| Multica API 未就緒 | 指令無法串接 | 中 | Mock API 開發；API 合約先行 |
| Telegram API 速率限制 | 批次通知被封鎖 | 低 | 佇列 + 指數退避 + 分散發送 |
| Group Topics 權限問題 | Bot 無法建立 Topic | 低 | 需 admin 權限；文件說明設定步驟 |
| WebSocket 連線不穩 | 通知延遲 | 中 | 自動重連 + 心跳檢查 + 備用 polling |
| 訊息格式跨平台差異 | Android/iOS 顯示不一 | 低 | 避免複雜 Unicode；測試雙平台 |

### 8.4 依賴

| 依賴項 | 提供方 | 狀態 | 替代方案 |
|--------|--------|------|---------|
| Multica Backend API | Backend Team | 開發中 | Mock Server |
| WebSocket 事件流 | Backend Team | 規劃中 | Polling fallback |
| Telegram Supergroup | 運維 | 已建立 | — |
| Bot Admin 權限 | @BotFather | 已設定 | — |
| python-telegram-bot ≥21.0 | PyPI | 穩定 | — |
| websockets ≥12.0 | PyPI | 穩定 | — |

---

## 附錄：bot.py 入口結構

```python
# src/telegram/bot.py
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters,
)
from .handlers.commands import (
    cmd_start, cmd_help, cmd_status, cmd_board,
    cmd_assign, cmd_cost, cmd_approve, cmd_blockers,
    cmd_notify, cmd_workspace, cmd_daily,
)
from .handlers.messages import handle_message
from .handlers.callbacks import handle_callback
from .notifications import NotificationListener

def create_telegram_app(token: str, multica_api_url: str, ws_url: str):
    """建立 Telegram Bot Application。"""
    app = ApplicationBuilder().token(token).build()

    # Slash 指令（11 個）
    commands = [
        ("start", cmd_start), ("help", cmd_help),
        ("status", cmd_status), ("board", cmd_board),
        ("assign", cmd_assign), ("cost", cmd_cost),
        ("approve", cmd_approve), ("blockers", cmd_blockers),
        ("notify", cmd_notify), ("workspace", cmd_workspace),
        ("daily", cmd_daily),
    ]
    for name, handler in commands:
        app.add_handler(CommandHandler(name, handler))

    # Callback Query（InlineKeyboard）
    app.add_handler(CallbackQueryHandler(handle_callback))

    # 自然語言 fallback
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
```

# Multica 後台管理面板 — 詳細 Spec 與執行計畫

> 日期：2026-06-17
> 範圍：P0 + P1 頁面（Dashboard、Session Inspector、Cost Analytics、Audit Log、Queue Manager）
> 技術棧：Next.js 16 App Router + Go Backend + PostgreSQL + WebSocket

---

## 架構設計

```
┌─────────────────────────────────────────────────────────────┐
│ Next.js 16 App Router (apps/web)                            │
│                                                             │
│  /admin/dashboard        ← 總覽儀表板                       │
│  /admin/sessions/[id]    ← Agent 對話檢視                   │
│  /admin/costs            ← 成本追蹤                         │
│  /admin/audit            ← 審計日誌                         │
│  /admin/queue            ← 任務佇列管理                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Go Backend (server/)                                        │
│                                                             │
│  GET  /api/admin/dashboard/stats                            │
│  GET  /api/admin/dashboard/trends                           │
│  GET  /api/admin/dashboard/live                             │
│  GET  /api/admin/sessions/:agent_id                         │
│  GET  /api/admin/sessions/:agent_id/:session_id             │
│  GET  /api/admin/costs?range=7d&group_by=agent              │
│  GET  /api/admin/costs/export?format=csv                    │
│  GET  /api/admin/audit?actor=&action=&from=&to=             │
│  GET  /api/admin/queue                                      │
│  PATCH /api/admin/queue/:issue_id/priority                  │
│  POST /api/admin/queue/batch                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ PostgreSQL 17                                               │
│                                                             │
│  agent_sessions          ← 對話記錄                         │
│  session_turns           ← 每輪 prompt/response             │
│  cost_records            ← token 消耗記錄                   │
│  audit_events            ← 審計事件                         │
│  issue_queue_priority    ← 佇列優先級覆寫                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 一、Dashboard（總覽儀表板）

### 頁面路由

```
/admin/dashboard
```

### API 端點

#### GET /api/admin/dashboard/stats

```json
{
  "active_agents": 5,
  "running_tasks": 3,
  "completed_today": 12,
  "avg_completion_minutes": 18.5,
  "total_cost_today_usd": 4.32,
  "runtimes_online": 2,
  "runtimes_total": 3
}
```

#### GET /api/admin/dashboard/trends?days=7

```json
{
  "dates": ["2026-06-11", "2026-06-12", ...],
  "completed": [8, 12, 15, 9, 11, 14, 12],
  "failed": [1, 0, 2, 0, 1, 0, 1],
  "cost_usd": [3.2, 4.1, 5.5, 2.8, 3.9, 4.7, 4.3]
}
```

#### GET /api/admin/dashboard/live

即時推送事件：
```json
{"type": "agent_status", "agent": "coder-agent", "status": "executing", "issue_id": 42}
{"type": "task_completed", "agent": "qa-agent", "issue_id": 38, "duration_ms": 45000}
{"type": "runtime_health", "runtime": "local-macbook", "cpu": 45, "memory": 62}
```

### 前端元件

```
AdminDashboard/
├── KpiCards.tsx           # 4 張 KPI 卡片（active agents, running, completed, avg time）
├── CostBadge.tsx          # 今日費用 badge（超閾值變紅）
├── TrendChart.tsx         # 7 天完成量折線圖（Recharts）
├── AgentActivityGrid.tsx  # Agent 狀態網格（即時 WS 更新）
├── RuntimeStatusBar.tsx   # Runtime 健康橫條
└── RecentActivity.tsx     # 最近 10 筆動態（滾動列表）
```

### 資料庫

不需新表 — 從現有 `issues`、`agent_runs`、`runtimes` 表聚合。

---

## 二、Agent Session Inspector

### 頁面路由

```
/admin/sessions                    # Agent 列表 + 最近 sessions
/admin/sessions/[agent_id]         # 該 Agent 的所有 sessions
/admin/sessions/[agent_id]/[sid]   # 單一 session 詳情（對話回放）
```

### API 端點

#### GET /api/admin/sessions/:agent_id

```json
{
  "agent": "coder-agent",
  "sessions": [
    {
      "id": "sess_abc123",
      "issue_id": 42,
      "started_at": "2026-06-17T08:00:00Z",
      "ended_at": "2026-06-17T08:18:00Z",
      "status": "completed",
      "total_turns": 24,
      "total_tokens": 45000,
      "cost_usd": 0.89
    }
  ]
}
```

#### GET /api/admin/sessions/:agent_id/:session_id

```json
{
  "session_id": "sess_abc123",
  "agent": "coder-agent",
  "issue_id": 42,
  "turns": [
    {
      "index": 0,
      "role": "system",
      "content": "You are coder-agent...",
      "timestamp": "2026-06-17T08:00:00Z",
      "tokens": 250
    },
    {
      "index": 1,
      "role": "user",
      "content": "建立 Express.js REST API...",
      "timestamp": "2026-06-17T08:00:01Z",
      "tokens": 120
    },
    {
      "index": 2,
      "role": "assistant",
      "content": "I'll create the API...",
      "tool_calls": [
        {"name": "write_file", "input": {"path": "src/app.js"}, "output": "created", "duration_ms": 450}
      ],
      "timestamp": "2026-06-17T08:00:15Z",
      "tokens": 3200
    }
  ],
  "summary": {
    "total_tokens": 45000,
    "total_tool_calls": 18,
    "files_created": 5,
    "files_modified": 3
  }
}
```

#### POST /api/admin/sessions/:agent_id/:session_id/intervene

```json
{"action": "abort" | "retry" | "inject_message", "message": "optional"}
```

### 前端元件

```
SessionInspector/
├── SessionList.tsx         # Session 卡片列表（帶搜尋/篩選）
├── ConversationView.tsx    # 對話回放（氣泡式 + 語法高亮）
├── ToolCallPanel.tsx       # Tool 呼叫展開面板（input/output/duration）
├── TokenMeter.tsx          # Token 使用量進度條
├── TimelineMarkers.tsx     # 時間軸標記（決策點、錯誤、重試）
└── InterveneModal.tsx      # 管理員介入操作 modal
```

### 資料庫

```sql
CREATE TABLE agent_sessions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id     UUID NOT NULL REFERENCES agents(id),
    issue_id     UUID REFERENCES issues(id),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    status       TEXT NOT NULL DEFAULT 'running', -- running | completed | failed | aborted
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at     TIMESTAMPTZ,
    total_tokens INT DEFAULT 0,
    cost_usd     NUMERIC(10,4) DEFAULT 0,
    metadata     JSONB DEFAULT '{}'
);

CREATE TABLE session_turns (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES agent_sessions(id),
    index        INT NOT NULL,
    role         TEXT NOT NULL, -- system | user | assistant | tool
    content      TEXT,
    tool_calls   JSONB DEFAULT '[]',
    tokens       INT DEFAULT 0,
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_session_turns_session ON session_turns(session_id, index);
```

---

## 三、Cost Analytics

### 頁面路由

```
/admin/costs
```

### API 端點

#### GET /api/admin/costs?range=7d&group_by=agent

```json
{
  "range": "7d",
  "total_usd": 28.45,
  "total_tokens": 1250000,
  "by_agent": [
    {"agent": "coder-agent", "cost_usd": 12.30, "tokens": 580000, "tasks": 15},
    {"agent": "ai-dev-agent", "cost_usd": 8.90, "tokens": 390000, "tasks": 8},
    {"agent": "qa-agent", "cost_usd": 4.50, "tokens": 180000, "tasks": 12},
    {"agent": "pm-agent", "cost_usd": 2.75, "tokens": 100000, "tasks": 20}
  ],
  "by_model": [
    {"model": "claude-4-opus", "cost_usd": 18.20, "tokens": 450000},
    {"model": "claude-4-sonnet", "cost_usd": 8.50, "tokens": 650000},
    {"model": "gpt-5-mini", "cost_usd": 1.75, "tokens": 150000}
  ],
  "daily": [
    {"date": "2026-06-11", "cost_usd": 3.20, "tokens": 150000},
    ...
  ]
}
```

#### GET /api/admin/costs/export?format=csv&range=30d

回傳 CSV 下載。

#### POST /api/admin/costs/budget

```json
{"daily_limit_usd": 30, "weekly_limit_usd": 150, "alert_threshold_pct": 80}
```

### 前端元件

```
CostAnalytics/
├── CostOverview.tsx        # 總費用 + 趨勢 sparkline
├── AgentCostTable.tsx      # 按 Agent 排序的費用表格
├── ModelBreakdown.tsx      # 模型用量圓餅圖
├── DailyCostChart.tsx      # 每日費用柱狀圖
├── BudgetSettings.tsx      # 預算設定 + 警報閾值
└── ExportButton.tsx        # CSV 匯出按鈕
```

### 資料庫

```sql
CREATE TABLE cost_records (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    agent_id     UUID NOT NULL REFERENCES agents(id),
    session_id   UUID REFERENCES agent_sessions(id),
    issue_id     UUID REFERENCES issues(id),
    model        TEXT NOT NULL,
    input_tokens INT NOT NULL DEFAULT 0,
    output_tokens INT NOT NULL DEFAULT 0,
    cost_usd     NUMERIC(10,6) NOT NULL,
    recorded_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_cost_records_workspace_date ON cost_records(workspace_id, recorded_at);
CREATE INDEX idx_cost_records_agent ON cost_records(agent_id, recorded_at);

CREATE TABLE budget_configs (
    workspace_id     UUID PRIMARY KEY REFERENCES workspaces(id),
    daily_limit_usd  NUMERIC(10,2),
    weekly_limit_usd NUMERIC(10,2),
    alert_threshold  INT DEFAULT 80
);
```

---

## 四、Audit Log

### 頁面路由

```
/admin/audit
```

### API 端點

#### GET /api/admin/audit?actor=&action=&resource=&from=&to=&page=1&limit=50

```json
{
  "total": 1250,
  "page": 1,
  "events": [
    {
      "id": "evt_001",
      "actor": {"type": "human", "id": "user_123", "name": "paddyyang"},
      "action": "agent.created",
      "resource": {"type": "agent", "id": "agt_456", "name": "coder-agent"},
      "details": {"provider": "claude-code", "runtime": "local-macbook"},
      "ip": "118.163.12.151",
      "timestamp": "2026-06-17T08:00:00Z"
    },
    {
      "id": "evt_002",
      "actor": {"type": "agent", "id": "agt_789", "name": "pm-agent"},
      "action": "issue.assigned",
      "resource": {"type": "issue", "id": "iss_42", "title": "建立 REST API"},
      "details": {"assignee": "coder-agent"},
      "timestamp": "2026-06-17T08:01:00Z"
    }
  ]
}
```

### 事件類型

| Category | Actions |
|----------|---------|
| auth | `login`, `logout`, `token_refresh`, `api_key_created` |
| agent | `created`, `updated`, `deleted`, `started`, `stopped` |
| issue | `created`, `assigned`, `status_changed`, `completed`, `failed` |
| squad | `created`, `member_added`, `member_removed` |
| runtime | `connected`, `disconnected`, `restarted` |
| settings | `workspace_updated`, `budget_changed`, `permission_changed` |
| admin | `intervene`, `abort_session`, `force_retry` |

### 前端元件

```
AuditLog/
├── AuditFilters.tsx        # 篩選列（actor/action/resource/daterange）
├── AuditTable.tsx          # 事件表格（虛擬滾動 for 大量資料）
├── EventDetail.tsx         # 點擊展開詳情
├── ActorBadge.tsx          # Human（藍）/ Agent（綠）/ System（灰）badge
└── ExportAudit.tsx         # JSON/CSV 匯出（合規用）
```

### 資料庫

```sql
CREATE TABLE audit_events (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    actor_type   TEXT NOT NULL, -- human | agent | system
    actor_id     UUID,
    actor_name   TEXT,
    action       TEXT NOT NULL,
    resource_type TEXT,
    resource_id  UUID,
    resource_name TEXT,
    details      JSONB DEFAULT '{}',
    ip_address   INET,
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_workspace_time ON audit_events(workspace_id, timestamp DESC);
CREATE INDEX idx_audit_actor ON audit_events(actor_type, actor_id);
CREATE INDEX idx_audit_action ON audit_events(action);
```

---

## 五、Queue Manager

### 頁面路由

```
/admin/queue
```

### API 端點

#### GET /api/admin/queue?status=pending&sort=priority

```json
{
  "total": 8,
  "items": [
    {
      "issue_id": "iss_42",
      "title": "建立用戶認證模組",
      "priority": 1,
      "status": "pending",
      "created_at": "2026-06-17T07:00:00Z",
      "waiting_minutes": 62,
      "suggested_agent": "coder-agent",
      "blocked_by": null,
      "labels": ["backend", "auth"]
    }
  ]
}
```

#### PATCH /api/admin/queue/:issue_id/priority

```json
{"priority": 1}  // 1=urgent, 2=high, 3=normal, 4=low
```

#### POST /api/admin/queue/batch

```json
{
  "action": "assign" | "cancel" | "retry" | "set_priority",
  "issue_ids": ["iss_42", "iss_43", "iss_44"],
  "params": {"agent": "coder-agent"}  // for assign
}
```

### 前端元件

```
QueueManager/
├── QueueTable.tsx          # 拖拽排序表格
├── PriorityBadge.tsx       # 優先級色彩標記（urgent 紅/high 橙/normal 藍/low 灰）
├── BatchActions.tsx        # 批量操作工具列（多選 + 動作）
├── BlockerGraph.tsx        # 阻塞關係圖（mini DAG）
├── AssignModal.tsx         # 指派 Agent modal（帶推薦）
└── QueueMetrics.tsx        # 佇列指標（平均等待時間、積壓量）
```

### 資料庫

```sql
-- 擴充現有 issues 表（加欄位）
ALTER TABLE issues ADD COLUMN queue_priority INT DEFAULT 3;
ALTER TABLE issues ADD COLUMN blocked_by UUID REFERENCES issues(id);

CREATE INDEX idx_issues_queue ON issues(workspace_id, status, queue_priority) WHERE status = 'pending';
```

---

## 執行計畫

### Phase 1：基礎建設（Week 1）

| 天 | 任務 | 產出 |
|----|------|------|
| D1 | DB migration（4 張新表 + 2 個 ALTER） | `server/migrations/0XX_admin_tables.sql` |
| D1 | Go backend：admin router + middleware（鑑權） | `server/internal/api/admin/` |
| D2 | Dashboard API（3 端點） | stats + trends + WS live |
| D2 | Dashboard 前端頁面 | `apps/web/app/admin/dashboard/` |
| D3 | Session Inspector API（3 端點） | list + detail + intervene |
| D3 | Session 資料收集 hook（daemon 側） | agent_sessions + session_turns 寫入 |

### Phase 2：成本與審計（Week 2）

| 天 | 任務 | 產出 |
|----|------|------|
| D4 | Cost 記錄 hook（每次 LLM 呼叫後寫入） | cost_records 自動記錄 |
| D4 | Cost Analytics API + 前端 | `/admin/costs` 完整頁面 |
| D5 | Audit event emitter（Go middleware） | 所有 mutation 自動記錄 |
| D5 | Audit Log API + 前端 | `/admin/audit` 完整頁面 |

### Phase 3：佇列管理 + 整合（Week 3）

| 天 | 任務 | 產出 |
|----|------|------|
| D6 | Queue Manager API + 前端 | `/admin/queue` 完整頁面 |
| D6 | 批量操作 + 拖拽排序 | BatchActions + DnD |
| D7 | Session Inspector 前端（對話回放 UI） | ConversationView + ToolCallPanel |
| D7 | E2E 測試 + 文件 | Playwright tests + API docs |

### Phase 4：打磨（Week 4）

| 天 | 任務 | 產出 |
|----|------|------|
| D8 | WebSocket 即時更新 Dashboard | live agent status |
| D8 | 預算警報通知（email + webhook） | budget alert system |
| D9 | 權限控制（admin/member 分級） | RBAC for admin pages |
| D9 | 暗色/亮色主題切換 | theme support |
| D10 | 效能優化 + 壓力測試 | 虛擬滾動、查詢優化 |

---

## 檔案結構（新增）

```
apps/web/app/admin/
├── layout.tsx                  # Admin layout（側邊導航）
├── dashboard/
│   ├── page.tsx
│   └── components/
│       ├── KpiCards.tsx
│       ├── TrendChart.tsx
│       ├── AgentActivityGrid.tsx
│       └── RuntimeStatusBar.tsx
├── sessions/
│   ├── page.tsx               # Agent 列表
│   ├── [agentId]/
│   │   ├── page.tsx           # Sessions 列表
│   │   └── [sessionId]/
│   │       └── page.tsx       # 對話回放
│   └── components/
│       ├── ConversationView.tsx
│       ├── ToolCallPanel.tsx
│       └── TokenMeter.tsx
├── costs/
│   ├── page.tsx
│   └── components/
│       ├── AgentCostTable.tsx
│       ├── ModelBreakdown.tsx
│       └── DailyCostChart.tsx
├── audit/
│   ├── page.tsx
│   └── components/
│       ├── AuditFilters.tsx
│       └── AuditTable.tsx
└── queue/
    ├── page.tsx
    └── components/
        ├── QueueTable.tsx
        ├── BatchActions.tsx
        └── BlockerGraph.tsx

server/internal/api/admin/
├── router.go                   # Admin 路由群組
├── middleware.go               # Admin 鑑權 middleware
├── dashboard.go                # Dashboard handlers
├── sessions.go                 # Session Inspector handlers
├── costs.go                    # Cost Analytics handlers
├── audit.go                    # Audit Log handlers
└── queue.go                    # Queue Manager handlers

server/migrations/
├── 0XX_create_agent_sessions.sql
├── 0XX_create_session_turns.sql
├── 0XX_create_cost_records.sql
├── 0XX_create_audit_events.sql
└── 0XX_add_queue_fields.sql
```

---

## 驗收標準

| 頁面 | 驗收條件 |
|------|---------|
| Dashboard | 打開即顯示即時資料、WS 斷線自動重連、mobile 響應式 |
| Session Inspector | 能回放任何 agent 的完整對話、tool call 可展開、管理員能中斷 |
| Cost Analytics | 數據與實際 API 費用誤差 < 5%、CSV 匯出正確、預算警報觸發 |
| Audit Log | 所有 mutation 都有記錄、篩選 < 200ms 回應、匯出 SOC2 格式 |
| Queue Manager | 拖拽排序即時生效、批量操作原子性、阻塞關係正確顯示 |

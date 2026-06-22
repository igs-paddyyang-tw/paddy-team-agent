---
title: "Ark Web Dashboard"
status: implemented
type: spec
author: paddyyang
created: 2026-06-17
---

# Ark Web Dashboard — 前端規格書

## 1. 問題陳述

目前 Ark Agent Platform 的操作介面只有 Telegram Bot 和 HTTP API，缺乏視覺化管理後台。需要一個 Web Dashboard 提供：
- 即時監控（Agent 狀態、任務進度）
- 資料視覺化（費用趨勢、完成率圖表）
- 批量管理（佇列排序、批量指派）
- Session 回放（debug Agent 行為）

---

## 2. 技術棧

| 面向 | 選擇 | 理由 |
|------|------|------|
| Framework | Next.js 16 (App Router) | 對齊 Multica 原生架構 |
| UI Library | shadcn/ui + Tailwind CSS 4 | 快速開發 + 暗色主題 |
| 圖表 | Recharts | React 生態、SSR 友好 |
| 即時通訊 | WebSocket (native) | 對接 `/api/ws/events` |
| Data Fetching | SWR（client）+ RSC（server） | 混合策略 |
| 狀態管理 | React Context + SWR cache | 輕量、不引入 Redux |
| 認證 | API Key header | 對齊 Backend RBAC |
| 部署 | Docker（`Dockerfile.web`）| 獨立容器 |

---

## 3. 頁面路由

```
/                          → redirect /admin/dashboard
/admin
├── /dashboard             → 總覽儀表板
├── /agents                → Agent 列表 + 詳情
├── /agents/[id]           → Agent Profile
├── /sessions              → Session 列表
├── /sessions/[id]         → 對話回放（Session Inspector）
├── /issues                → Issue Board（Kanban）
├── /costs                 → 費用分析
├── /audit                 → 審計日誌
├── /queue                 → 佇列管理
└── /settings              → 系統設定
```

---

## 4. 頁面規格

### 4.1 Dashboard (`/admin/dashboard`)

**資料來源**：`GET /api/admin/dashboard/stats` + `GET /api/admin/dashboard/trends` + WS live

**元件：**

```tsx
interface DashboardPageProps {}

// KPI 卡片
interface KpiCardProps {
  label: string
  value: number | string
  change?: number        // vs 昨日 %
  format: 'number' | 'currency' | 'duration'
  icon: ReactNode
}

// 趨勢圖
interface TrendChartProps {
  data: { date: string; completed: number; failed: number; cost: number }[]
  days: 7 | 14 | 30
}

// Agent 狀態網格
interface AgentGridProps {
  agents: { id: string; name: string; role: string; status: 'idle' | 'busy' | 'offline' }[]
  onSelect: (id: string) => void
}

// 即時活動流
interface ActivityFeedProps {
  events: Event[]    // 最近 20 筆，WS 即時更新
}
```

**Layout：**
```
┌─────────────────────────────────────────────┐
│ [KPI] [KPI] [KPI] [KPI]                    │
├──────────────────────┬──────────────────────┤
│ TrendChart (7d)      │ AgentGrid            │
├──────────────────────┴──────────────────────┤
│ ActivityFeed (live)                          │
└─────────────────────────────────────────────┘
```

**Fetch 策略**：stats → RSC (revalidate 30s)；trends → SWR；live → WebSocket

---

### 4.2 Agent Profile (`/admin/agents/[id]`)

**資料來源**：`GET /api/agents/{id}` + `GET /api/admin/sessions?agent_id={id}`

```tsx
interface AgentProfileProps {
  agent: {
    id: string
    name: string
    role: 'admin' | 'leader' | 'worker'
    provider: string
    status: string
    model: string
    working_dir: string
    created_at: string
  }
  stats: {
    total_tasks: number
    completed: number
    failed: number
    avg_duration_s: number
    total_cost_usd: number
  }
  recent_sessions: Session[]
}
```

---

### 4.3 Session Inspector (`/admin/sessions/[id]`)

**資料來源**：`GET /api/admin/sessions/{id}`

```tsx
interface SessionViewProps {
  session: {
    id: string
    agent_id: string
    status: 'running' | 'completed' | 'failed'
    started_at: string
    ended_at: string | null
    total_tokens: number
    cost_usd: number
    output: string
  }
  turns: Turn[]
}

interface Turn {
  id: string
  idx: number
  role: 'system' | 'user' | 'assistant' | 'tool'
  content: string
  tool_calls: ToolCall[]
  tokens: number
  timestamp: string
}

interface ToolCall {
  name: string
  input: Record<string, any>
  output: string
  duration_ms: number
}
```

**元件：**
```
┌─────────────────────────────────────────────┐
│ Session Header (agent + status + cost)       │
├─────────────────────────────┬───────────────┤
│ ConversationView            │ TokenMeter    │
│ (氣泡式，語法高亮)          │ (進度條)      │
│                             │               │
│ [user] 建立 API             │ ████░░ 60%   │
│ [assistant] 好的...         │               │
│   └ [tool] write_file       │ Timeline      │
│      input: {path:...}      │ (時間軸標記)  │
│      output: created        │               │
└─────────────────────────────┴───────────────┘
```

---

### 4.4 Costs (`/admin/costs`)

**資料來源**：`GET /api/admin/costs?range=7d`

```tsx
interface CostsPageProps {
  summary: {
    total_usd: number
    total_records: number
    by_agent: Record<string, number>
    by_model: Record<string, number>
  }
  daily: { date: string; cost: number }[]
  budget: { daily_limit_usd: number; alert_threshold: number }
}
```

**元件：**
- `CostOverview` — 總費用 + sparkline
- `AgentCostBar` — 按 Agent 的水平柱狀圖
- `ModelPie` — 按 Model 的圓餅圖
- `DailyChart` — 每日費用折線圖
- `BudgetAlert` — 超閾值紅色警示

---

### 4.5 Audit (`/admin/audit`)

**資料來源**：`GET /api/admin/audit?limit=100`

```tsx
interface AuditPageProps {
  total: number
  events: AuditEvent[]
}

interface AuditEvent {
  id: string
  actor_type: 'human' | 'agent' | 'system'
  actor_name: string
  action: string
  resource_type: string
  resource_name: string
  details: string
  timestamp: string
}
```

**元件：**
- `AuditFilters` — actor / action / date range 篩選
- `AuditTable` — 虛擬滾動表格（>1000 筆不卡頓）
- `ActorBadge` — human(藍) / agent(綠) / system(灰)

---

### 4.6 Queue (`/admin/queue`)

**資料來源**：`GET /api/admin/queue`

```tsx
interface QueueItem {
  id: string
  title: string
  priority: 1 | 2 | 3 | 4
  status: 'pending' | 'assigned'
  assignee: string | null
  created_at: string
}
```

**元件：**
- `QueueTable` — 拖拽排序（dnd-kit）
- `PriorityBadge` — 🔴🟠🔵⚪
- `BatchToolbar` — 多選 + 批量操作（指派/取消/改優先級）
- `AssignModal` — Agent 選擇 dropdown

---

## 5. WebSocket 即時更新

```tsx
// hooks/useEventStream.ts
function useEventStream() {
  const [events, setEvents] = useState<Event[]>([])

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:33333/api/ws/events')
    ws.onmessage = (msg) => {
      const event = JSON.parse(msg.data)
      setEvents(prev => [event, ...prev].slice(0, 50))

      // 觸發 SWR revalidate
      if (event.type === 'task.completed') mutate('/api/admin/dashboard/stats')
      if (event.type === 'cost.recorded') mutate('/api/admin/costs')
    }
    return () => ws.close()
  }, [])

  return events
}
```

使用頁面：Dashboard（AgentGrid + ActivityFeed）

---

## 6. 認證流程

```
1. 使用者開啟 /admin → 檢查 localStorage 的 API Key
2. 無 key → 顯示登入頁（輸入 API Key）
3. 有 key → 每個 fetch 帶 header: X-API-Key
4. 401 → 清除 key → 重導到登入頁
```

```tsx
// lib/api.ts
const api = {
  get: (path: string) =>
    fetch(`${API_BASE}${path}`, {
      headers: { 'X-API-Key': getApiKey() }
    }).then(r => {
      if (r.status === 401) { clearApiKey(); redirect('/login') }
      return r.json()
    })
}
```

---

## 7. 響應式斷點

| 斷點 | 寬度 | Layout |
|------|------|--------|
| Mobile | < 768px | 單欄、KPI 2x2、隱藏 sidebar |
| Tablet | 768-1024px | 側邊欄收合、圖表縮小 |
| Desktop | > 1024px | 完整 sidebar + 雙欄內容 |

---

## 8. 主題

暗色主題（預設）：

```css
:root {
  --bg-primary: #0f172a;
  --bg-card: #1e293b;
  --text-primary: #e2e8f0;
  --text-muted: #94a3b8;
  --accent: #22d3ee;
  --success: #22c55e;
  --danger: #ef4444;
  --warning: #f59e0b;
  --border: #334155;
}
```

---

## 9. 檔案結構

```
apps/web/
├── app/
│   ├── layout.tsx              # Root layout (暗色主題 + font)
│   ├── login/page.tsx          # API Key 登入
│   └── admin/
│       ├── layout.tsx          # Admin layout (sidebar + header)
│       ├── dashboard/page.tsx
│       ├── agents/
│       │   ├── page.tsx
│       │   └── [id]/page.tsx
│       ├── sessions/
│       │   ├── page.tsx
│       │   └── [id]/page.tsx
│       ├── issues/page.tsx
│       ├── costs/page.tsx
│       ├── audit/page.tsx
│       ├── queue/page.tsx
│       └── settings/page.tsx
├── components/
│   ├── ui/                     # shadcn/ui 元件
│   ├── dashboard/
│   │   ├── KpiCard.tsx
│   │   ├── TrendChart.tsx
│   │   ├── AgentGrid.tsx
│   │   └── ActivityFeed.tsx
│   ├── sessions/
│   │   ├── ConversationView.tsx
│   │   ├── ToolCallPanel.tsx
│   │   └── TokenMeter.tsx
│   ├── costs/
│   │   ├── CostOverview.tsx
│   │   ├── AgentCostBar.tsx
│   │   └── ModelPie.tsx
│   ├── audit/
│   │   ├── AuditFilters.tsx
│   │   └── AuditTable.tsx
│   └── queue/
│       ├── QueueTable.tsx
│       └── BatchToolbar.tsx
├── hooks/
│   ├── useEventStream.ts       # WebSocket
│   └── useApi.ts               # SWR wrapper
├── lib/
│   ├── api.ts                  # API client + auth
│   └── types.ts                # 共用 TypeScript types
├── package.json
├── tailwind.config.ts
└── next.config.ts
```

---

## 10. 驗收條件

| 頁面 | Pass 條件 |
|------|-----------|
| Dashboard | 首次載入 < 1s，KPI 即時正確，WS 事件 5s 內顯示 |
| Agent Profile | 顯示績效統計 + 最近 sessions |
| Session Inspector | 完整對話回放 + tool call 可展開 |
| Costs | 圖表渲染正確，CSV 匯出可下載 |
| Audit | 1000+ 筆虛擬滾動不卡頓，篩選 < 200ms |
| Queue | 拖拽排序即時生效，批量操作原子性 |
| 認證 | 無 key 顯示登入頁，錯 key 顯示 401 |
| 響應式 | Mobile/Tablet/Desktop 三斷點正確 |
| 暗色主題 | 所有頁面一致，無白色閃爍 |

---

## 11. 執行計畫

| 天 | 任務 | 產出 |
|----|------|------|
| D1 | 專案初始化（Next.js + shadcn + Tailwind） | `apps/web/` 骨架 |
| D2 | Admin layout（sidebar + header + auth） | layout.tsx + login |
| D3 | Dashboard（KPI + TrendChart + AgentGrid） | dashboard/page.tsx |
| D4 | WebSocket hook + ActivityFeed | hooks/useEventStream.ts |
| D5 | Sessions list + Inspector（ConversationView） | sessions/ |
| D6 | Costs（3 個圖表 + budget alert） | costs/page.tsx |
| D7 | Audit（filters + virtual scroll table） | audit/page.tsx |
| D8 | Queue（dnd-kit + batch toolbar） | queue/page.tsx |
| D9 | Agent Profile + Issues Board | agents/ + issues/ |
| D10 | 響應式 + 主題打磨 + E2E 測試 | 全頁面 |

**預估：2 週（10 工作天）**

---
title: "Web Dashboard 看板視圖強化"
type: onepager
status: in-progress
created: 2026-07-04
updated: 2026-07-04
language: zh-TW
author: leader-agent
ref: docs/specs/web-dashboard-spec.md
---

# Web Dashboard 看板視圖強化

## 問題陳述

目前 Web Dashboard 有 7 個頁面（Dashboard/Agents/Sessions/Costs/Audit/Queue/Settings），但缺少核心的 **Issue Board（看板視圖）**。現有 Queue 頁面只是表格列表，沒有 Kanban 拖拉、狀態流轉、即時更新等功能。

對比 Multica 的看板：Agent 跟人一樣在 Board 上被指派、追蹤進度、回報完成。我們目前的 issues API 已支援完整 CRUD + 狀態流轉，但前端沒有對應的視覺化看板。

## 目標

1. 新增 `/admin/issues` 頁面 — Kanban 看板視圖（4 欄：Pending → Assigned → In Progress → Done）
2. 支援拖拉排序 + 狀態流轉
3. WebSocket 即時更新（其他 Agent 完成任務時自動移動卡片）
4. 卡片顯示：標題、優先級、指派人、建立時間
5. 快速建立 Issue + 指派 Agent

## 非目標

- 不做多 Workspace（維持單一工作區）
- 不做 Sprint / Milestone 分組（未來再加）
- 不做拖拉排序的持久化（僅狀態欄位變更有意義）

## 現有基礎

### Backend API（已就緒 ✅）

| 端點 | 用途 |
|------|------|
| `GET /api/issues` | 列出所有 issues（支援 ?status= 篩選） |
| `POST /api/issues` | 建立 issue（title/description/priority/assignee） |
| `PATCH /api/issues/{id}/assign` | 指派 Agent |
| `PATCH /api/issues/{id}/complete` | 完成/失敗 |
| `DELETE /api/issues/{id}` | 刪除 |
| `WS /api/ws/events` | 即時事件推送（TASK_CREATED/ASSIGNED/COMPLETED/FAILED） |

### Frontend 現有元件

- `useEventStream` hook — 已接 WebSocket
- `fetcher` + `api` — SWR data fetching
- shadcn/ui Button — UI 基礎
- Tailwind 暗色主題 — 已統一

### 缺少的

- `/admin/issues` 頁面
- Kanban 元件（欄位 + 拖拉）
- Issue 卡片元件
- 建立 Issue Modal
- 即時卡片移動（WS 觸發 SWR mutate）

## 方案

### 技術選擇

| 面向 | 選擇 | 理由 |
|------|------|------|
| 拖拉庫 | `@dnd-kit/core` + `@dnd-kit/sortable` | 輕量、React 18 相容、a11y |
| 狀態管理 | SWR mutate + optimistic update | 保持現有模式 |
| 即時更新 | useEventStream → 過濾 TASK_* → SWR revalidate | 已有基建 |

### 頁面結構

```
/admin/issues
├── Header（搜尋 + 建立按鈕 + 篩選）
├── KanbanBoard
│   ├── Column: Pending（待處理）
│   ├── Column: Assigned（已指派）
│   ├── Column: In Progress（執行中）
│   └── Column: Completed（已完成）
└── CreateIssueModal（彈窗建立）
```

### 卡片設計

```
┌─────────────────────────────┐
│ 🔴 P1  ·  task-a1b2       │
│ 撰寫 API 端點              │
│                             │
│ 👤 coder-agent   ⏱ 2h ago  │
└─────────────────────────────┘
```

### 互動流程

1. **拖拉卡片** → `PATCH /api/issues/{id}/assign` 或 `/complete`
2. **點擊建立** → Modal → `POST /api/issues`
3. **WS 事件** → `TASK_COMPLETED` → 卡片從 In Progress 移到 Done（動畫）
4. **點擊卡片** → 展開詳情 sidebar

## 執行計畫

| # | 任務 | 大小 | 依賴 | 驗收 |
|---|------|------|------|------|
| 1 | 安裝 `@dnd-kit/core` + `@dnd-kit/sortable` | XS | 無 | package.json 更新 |
| 2 | 建立 `IssueCard` 元件 | S | 無 | 顯示標題/優先級/指派人/時間 |
| 3 | 建立 `KanbanColumn` 元件 | S | #2 | 接收 issues[] 渲染 + drop zone |
| 4 | 建立 `KanbanBoard` 元件 | M | #3 | 4 欄 + 拖拉跨欄 + API 呼叫 |
| 5 | 建立 `/admin/issues/page.tsx` | S | #4 | 整合 SWR + WS + Board |
| 6 | 建立 `CreateIssueModal` | S | #5 | 表單 → POST → Board 更新 |
| 7 | 即時更新整合 | S | #5 | WS event → 卡片自動移動 |
| 8 | 側邊欄加入 Issues 導航 | XS | #5 | layout.tsx 新增連結 |

**估計總量**：M（3-5 個檔案新增/修改）

## Backend 補充需求

目前 issues 表的 `status` 欄位支援：`pending` / `assigned` / `completed` / `failed`

需要新增一個狀態：**`in_progress`**

```sql
-- 需要在 issues 更新時允許 status = 'in_progress'
PATCH /api/issues/{id}/status  -- 新端點（通用狀態更新）
```

## 風險

| 風險 | 機率 | 緩解 |
|------|------|------|
| dnd-kit 與 Next.js SSR 衝突 | 中 | 用 `"use client"` + dynamic import |
| 即時更新閃爍 | 低 | Optimistic update + transition animation |
| Issue 數量過多效能 | 低 | 分頁或 Done 欄只顯示最近 20 筆 |

## 決策記錄（Grill Me 結果）

| # | 決策點 | 決定 | 理由 |
|---|--------|------|------|
| 1 | `in_progress` 觸發 | A2A Router 自動 | 真實反映 Agent 工作狀態 |
| 2 | Queue 頁面處理 | 移除，合併到 Issues 看板 | 避免兩入口看同一份資料 |
| 3 | Done 欄保留 | 最近 7 天 | 看板聚焦進行中 |
| 4 | 拖拉方向 | 只允許向右 | 狀態機有方向性 |
| 5 | 指派交互 | 拖到 Assigned 時彈 Agent 選擇框 | 建立時不強制選人 |
| 6 | 資料來源 | 同一張 issues 表 | TG/Web/API 統一 |
| 7 | 篩選功能 | 按 Agent 篩選 | 快速聚焦特定 Agent |
| 8 | 斷線處理 | 黃色 banner + 自動重連 | 使用者需知道資料可能過時 |
| 9 | 失敗處理 | 退回 Pending + 紅色標記 | 失敗需重新指派 |

## 成功指標

- [ ] `/admin/issues` 看板可見 4 欄
- [ ] 拖拉卡片可變更狀態
- [ ] 建立 Issue 後即時出現在 Pending 欄
- [ ] Agent 完成任務後卡片自動移到 Done（WS）
- [ ] 手機寬度響應式排版（單欄垂直）

## 與 Multica 的對標

| Multica 功能 | 本次實作 | 未來 |
|-------------|---------|------|
| Board view（看板） | ✅ 本次 | — |
| Issue comments | ❌ | v2 |
| Agent 自動建立 Issue | ❌ | v2 |
| Squads 群組指派 | ❌ | v3 |
| Autopilots（排程建立） | ⚠️ 有 scheduler 但未連 Board | v2 |

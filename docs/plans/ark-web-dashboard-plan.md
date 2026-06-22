---
title: "Ark Web Dashboard 執行計畫"
type: plan
version: "1.0"
status: draft
language: zh-TW
author: paddyyang
created: 2026-06-17
updated: 2026-06-17
related_design: "docs/designs/ark-web-dashboard-design.md"
related_spec: "docs/specs/ark-web-dashboard-spec.md"
---

# Ark Web Dashboard — 執行計畫

## 1. 摘要

建立 Ark Agent Platform 的 Web 管理後台，使用 Next.js 16 + shadcn/ui + Recharts，對接現有 Backend API（21 端點）和 WebSocket。預計 **2 週（10 天）** 交付 MVP，涵蓋 Dashboard、Sessions、Costs、Audit、Queue 五個核心頁面。

---

## 2. 里程碑（Milestones）

### Phase 1: 基礎建設（Day 1-2）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| Next.js 專案初始化 | coder-agent | 2h | 無 | `pnpm dev` 啟動成功 |
| shadcn/ui + Tailwind 暗色主題 | coder-agent | 2h | 專案 | 主題變數生效 |
| Admin Layout（sidebar + header） | coder-agent | 3h | UI | 所有路由有 sidebar |
| API client + Auth（login 頁） | ai-dev-agent | 3h | Backend | key 驗證 + 401 redirect |
| SWR + fetcher 設定 | ai-dev-agent | 1h | API client | SWR 可 fetch /api/health |

**Phase 1 交付物**：
- [ ] `apps/web/` 專案可運行
- [ ] 暗色主題 Admin Layout
- [ ] Login 頁 → API Key 驗證 → 進入 /admin
- [ ] SWR + API client 基礎設施

---

### Phase 2: Dashboard + WebSocket（Day 3-4）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| KpiCard × 4（RSC） | coder-agent | 2h | Layout | 顯示正確 stats |
| TrendChart（Recharts） | coder-agent | 3h | SWR | 7 天折線圖渲染 |
| AgentGrid | coder-agent | 2h | API | 狀態色點即時更新 |
| useEventStream hook | ai-dev-agent | 3h | WS | 連線 + 自動重連 |
| ActivityFeed（即時事件流） | coder-agent | 2h | WS hook | 事件到達 < 5s 顯示 |

**Phase 2 交付物**：
- [ ] Dashboard 完整頁面
- [ ] WebSocket 即時更新
- [ ] 自動重連機制

---

### Phase 3: Session Inspector（Day 5-6）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| Sessions 列表頁 | coder-agent | 2h | API | 按 agent 篩選 |
| ConversationView（氣泡 UI） | coder-agent | 4h | 無 | user/assistant 氣泡 + 語法高亮 |
| ToolCallAccordion | coder-agent | 2h | 無 | 點擊展開 input/output |
| TokenMeter | ai-dev-agent | 1h | 無 | 進度條正確 |
| Timeline markers | ai-dev-agent | 2h | 無 | 時間軸標記決策點 |

**Phase 3 交付物**：
- [ ] Session 回放完整可用
- [ ] Tool call 詳情可展開
- [ ] Token 使用量可視化

---

### Phase 4: Costs + Audit（Day 7-8）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| CostOverview + AgentCostBar | coder-agent | 3h | Recharts | 柱狀圖正確 |
| ModelPie（圓餅圖） | coder-agent | 1h | Recharts | 按 model 分佈 |
| DailyChart + BudgetAlert | coder-agent | 2h | API | 超閾值紅色 |
| AuditFilters | ai-dev-agent | 2h | 無 | actor/action/date 篩選 |
| AuditTable（虛擬滾動） | coder-agent | 3h | @tanstack/virtual | 1000 筆不卡 |
| CSV 匯出按鈕 | coder-agent | 1h | API | 下載 costs.csv |

**Phase 4 交付物**：
- [ ] Costs 頁面 3 個圖表
- [ ] Audit 虛擬滾動表格
- [ ] 費用 CSV 匯出

---

### Phase 5: Queue + Agent + 打磨（Day 9-10）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| QueueTable（dnd-kit 拖拽） | coder-agent | 3h | dnd-kit | 拖拽即時更新 priority |
| BatchToolbar（多選操作） | coder-agent | 2h | API | 批量指派/取消 |
| Agent Profile 頁 | coder-agent | 2h | API | 績效統計正確 |
| 響應式適配（3 斷點） | ai-dev-agent | 3h | 全部 | Mobile 可用 |
| E2E 測試（Playwright） | qa-agent | 4h | 全部 | 5 核心 flow 通過 |
| 效能優化 + Lighthouse | qa-agent | 2h | 全部 | LCP < 1.5s |

**Phase 5 交付物**：
- [ ] Queue 拖拽排序
- [ ] 全頁面響應式
- [ ] Playwright E2E 測試
- [ ] Lighthouse 90+ 分

---

## 3. 風險管理

| 風險 | 機率 | 影響 | 緩解策略 | 觸發條件 |
|------|------|------|----------|----------|
| Recharts SSR 問題 | M | M | dynamic import + ssr:false | 圖表 hydration error |
| WebSocket 跨域 | L | M | Next.js rewrites proxy | CORS 錯誤 |
| shadcn 暗色主題不完整 | L | L | 手動覆寫 CSS 變數 | 白色閃爍 |
| 虛擬滾動 + 篩選衝突 | M | M | server-side filter + limit | 篩選後空白 |
| Backend API 回應慢 | M | M | skeleton loading + SWR stale | >2s 回應 |

---

## 4. 驗證標準

| 類別 | 指標 | 目標 | 驗證方式 |
|------|------|------|----------|
| 效能 | LCP | < 1.5s | Lighthouse |
| 效能 | FID | < 100ms | Lighthouse |
| 即時性 | WS event → UI | < 5s | 手動計時 |
| 功能 | 頁面覆蓋 | 7/7 頁面可用 | 手動 + E2E |
| 響應式 | 3 斷點 | 全部正常 | Chrome DevTools |
| 穩定性 | 持續使用 | 1h 無 crash | 長時間測試 |
| Bundle | JS size | < 200KB (首頁) | `next build` 分析 |

---

## 5. 回滾計畫

| 觸發條件 | 回滾步驟 | 預估時間 |
|----------|----------|----------|
| Web 完全無法啟動 | 回退到純 TG + API 操作 | 0（不影響核心） |
| 某頁面 crash | 禁用該路由，其餘正常 | 1 min |
| WebSocket 持續斷線 | 禁用即時更新，改 SWR polling | 5 min |

---

## 6. 依賴與前置條件

### 技術依賴

| 套件 | 版本 | 用途 |
|------|------|------|
| next | 16.x | Framework |
| react | 19.x | UI |
| tailwindcss | 4.x | Styling |
| shadcn/ui | latest | 元件庫 |
| recharts | 2.x | 圖表 |
| swr | 2.x | Data fetching |
| @dnd-kit/core | 6.x | 拖拽 |
| @tanstack/react-virtual | 3.x | 虛擬滾動 |
| shiki | 1.x | 程式碼高亮（Session Inspector） |

### 前置條件

- Backend API 已部署且可存取（:33333）
- WebSocket `/api/ws/events` 可連線
- 至少 1 個 Agent 已建立（用於 Dashboard 測試）

### 人力

| 角色 | 負荷 |
|------|------|
| coder-agent | 100%（主力開發） |
| ai-dev-agent | 50%（WS/Auth/響應式） |
| qa-agent | 30% D1-8, 100% D9-10 |

---

## 7. 溝通計畫

| 事件 | 管道 | 頻率 |
|------|------|------|
| 每日進度 | TG /status | 每日 |
| Phase 完成 | TG 通知 | 每 2 天 |
| Demo | 螢幕截圖 → TG | D4 + D10 |
| Blocker | TG 即時 | 即時 |

# Multica 後台管理面板 — 網頁規格建議

> 基於 [multica-ai/multica](https://github.com/multica-ai/multica) 分析
> 日期：2026-06-17

---

## 專案概覽

**Multica** 是開源的 Managed Agents 平台，讓 AI Agent 成為真正的隊友。

| 層級 | 技術 |
|------|------|
| Frontend | Next.js 16 (App Router) |
| Backend | Go (Chi router, sqlc, gorilla/websocket) |
| Database | PostgreSQL 17 + pgvector |
| Runtime | Local daemon (kiro-cli, claude, codex 等) |

---

## 現有功能頁面（apps/web）

根據 README 和架構，Multica 已有：

| 頁面 | 功能 |
|------|------|
| Board | Kanban 看板（任務狀態流轉） |
| Issues | 任務建立/指派/追蹤 |
| Agents | Agent 管理（建立/設定 provider/runtime） |
| Runtimes | 計算環境管理（local daemon / cloud） |
| Squads | 團隊編組（leader + members 路由） |
| Autopilots | 排程自動化（cron/webhook/manual） |
| Skills | 可重用技能庫 |
| Settings | Workspace 設定 |

---

## 可新增的後台管理頁面規格

以下是 Multica 目前**缺少但適合加入**的後台管理頁面：

### 一、系統監控類

#### 1. 📊 Dashboard（總覽儀表板）

| 區塊 | 內容 |
|------|------|
| KPI 卡片 | 活躍 Agent 數、進行中任務、今日完成數、平均完成時間 |
| 任務趨勢圖 | 7 天/30 天完成量折線圖 |
| Agent 活動熱力圖 | 按小時顯示各 Agent 活動量 |
| 即時狀態 | Runtime 健康狀態（WebSocket 即時更新） |
| 費用預估 | 今日/本週 LLM token 消耗估算 |

**技術**：WebSocket 即時推送、Chart.js / Recharts、SSE fallback

#### 2. 📈 成本追蹤（Cost Analytics）

| 功能 | 說明 |
|------|------|
| 按 Agent 拆分 | 各 Agent 的 token 消耗、API 費用 |
| 按任務拆分 | 每個 Issue 消耗的計算資源 |
| 日/週/月報表 | 可匯出 CSV |
| 預算警報 | 超過閾值時通知 |
| 模型用量比較 | Claude vs Codex vs Gemini 費用對比 |

#### 3. 📋 審計日誌（Audit Log）

| 功能 | 說明 |
|------|------|
| 操作記錄 | 誰（human/agent）做了什麼、何時 |
| 篩選器 | 按 actor/action/resource/time 篩選 |
| 安全事件 | 登入/登出/權限變更 |
| 匯出 | JSON/CSV 匯出（合規需求） |

---

### 二、Agent 管理類

#### 4. 🤖 Agent 詳情頁（Agent Profile）

| 區塊 | 內容 |
|------|------|
| 基本資訊 | 名稱、Provider、Runtime、狀態 |
| 績效統計 | 完成率、平均耗時、失敗率 |
| 活動時間線 | 最近 50 筆動作 |
| Skill 清單 | 該 Agent 擁有的技能 |
| 設定 | 模型選擇、上下文窗口、重試策略 |

#### 5. 🧠 Agent 對話檢視（Session Inspector）

| 功能 | 說明 |
|------|------|
| 對話回放 | 完整的 prompt/response 歷史 |
| Tool 呼叫追蹤 | 每次 tool use 的輸入/輸出 |
| Token 計數 | 每輪的 token 使用量 |
| 分支點標記 | Agent 決策分歧的關鍵時刻 |
| 介入操作 | 管理員可中斷/修正/重試 |

#### 6. 👥 Squad 編輯器（Squad Builder）

| 功能 | 說明 |
|------|------|
| 拖拽組隊 | 視覺化拖拽 Agent 到 Squad |
| Leader 設定 | 指定 leader + 路由策略 |
| 能力矩陣 | 自動分析 Squad 覆蓋的 Skill |
| 模擬派工 | 輸入任務描述，預覽 leader 會派給誰 |

---

### 三、任務管理類

#### 7. 📋 任務佇列管理（Queue Manager）

| 功能 | 說明 |
|------|------|
| 待分配佇列 | 尚未指派的 Issue 清單 |
| 優先級調整 | 拖拽排序/手動設定 |
| 批量操作 | 批量指派、批量取消、批量重試 |
| 阻塞分析 | 顯示被 blocker 卡住的任務鏈 |

#### 8. 🔄 Autopilot 編輯器

| 功能 | 說明 |
|------|------|
| 視覺化 Cron | 互動式 cron 表達式產生器 |
| Webhook 設定 | URL + secret + retry 策略 |
| 執行歷史 | 過去 N 次觸發的結果 |
| 模板庫 | 預設 autopilot 模板（standup、code review、audit） |

---

### 四、開發者工具類

#### 9. 🔧 Runtime 診斷（Runtime Health）

| 功能 | 說明 |
|------|------|
| 即時指標 | CPU/Memory/Disk（daemon 回報） |
| CLI 偵測 | 可用的 Agent CLI 版本清單 |
| 連線品質 | WebSocket 延遲、斷線次數 |
| 日誌串流 | 即時 tail daemon 日誌 |
| 遠端操作 | 重啟 daemon、更新 CLI |

#### 10. 📝 Skill 編輯器（Skill Studio）

| 功能 | 說明 |
|------|------|
| 線上編輯 | Monaco Editor 編輯 Skill 定義 |
| 版本管理 | Skill 版本歷史 + diff |
| 測試沙盒 | 輸入測試參數、即時執行 |
| 使用統計 | 哪些 Agent 用了哪些 Skill、成功率 |
| 市集 | 社群共享 Skill（安裝/發佈） |

#### 11. 🔑 API 金鑰管理（API Keys）

| 功能 | 說明 |
|------|------|
| 金鑰 CRUD | 建立/撤銷/旋轉 |
| 權限範圍 | 細粒度 scope 設定 |
| 使用量追蹤 | 每個金鑰的呼叫次數/最後使用時間 |
| Rate Limit | 自訂速率限制 |

---

### 五、協作類

#### 12. 💬 Team Feed（團隊動態流）

| 功能 | 說明 |
|------|------|
| 統一動態流 | Human + Agent 所有活動合併顯示 |
| @mention | 人可以 @agent，agent 可以 @人 |
| 討論串 | Issue 內的對話（類 GitHub Discussion） |
| 通知中心 | 聚合所有需要注意的事項 |

#### 13. 📊 週報產生器（Weekly Report）

| 功能 | 說明 |
|------|------|
| 自動彙總 | 本週完成任務、程式碼變更、blocker |
| 團隊績效 | Human vs Agent 產出對比 |
| 趨勢分析 | 與上週比較 |
| 一鍵分享 | Slack/Email/Markdown 匯出 |

---

## 優先級建議

| 優先級 | 頁面 | 理由 |
|--------|------|------|
| 🔴 P0 | Dashboard | 系統入口，用戶第一印象 |
| 🔴 P0 | Agent Session Inspector | debug 必備，目前完全黑箱 |
| 🟡 P1 | Cost Analytics | 企業客戶硬需求 |
| 🟡 P1 | Audit Log | 合規需求（SOC2） |
| 🟡 P1 | Queue Manager | 大量任務時的管理痛點 |
| 🟢 P2 | Runtime Health | Ops 工具 |
| 🟢 P2 | Skill Studio | 開發者體驗 |
| 🟢 P2 | Squad Builder | 大型團隊才需要 |
| 🔵 P3 | Team Feed | 社交功能 |
| 🔵 P3 | Weekly Report | nice-to-have |
| 🔵 P3 | API Keys | 已有但可強化 |

---

## 技術棧建議（與 Multica 現有架構對齊）

| 面向 | 選擇 | 理由 |
|------|------|------|
| Framework | Next.js 16 App Router | 對齊現有 apps/web |
| UI Library | 現有 UI（推測 shadcn/ui） | 保持一致 |
| 圖表 | Recharts / Tremor | React 生態，SSR 友好 |
| 即時通訊 | WebSocket（gorilla） | 已有 infra |
| 狀態管理 | React Server Components + SWR | Next.js 慣例 |
| 認證 | 現有 auth 系統 | 對齊 Workspace 權限 |

---

## 下一步

1. 確認你想先做哪幾個頁面
2. 我產出對應的 spec（API 端點 + 前端元件 + 資料模型）
3. 拆解為可執行的開發任務

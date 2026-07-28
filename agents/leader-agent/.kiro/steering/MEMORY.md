# 🧠 leader-agent 專案記憶

> 每完成一個段落必須更新。

---

## 專案快照

- **團隊：** AI Team Agent（5 人）
- **建立日期：** 2026-06-17
- **狀態：** 🟢 開發中（優化階段）
- **平台入口：** Telegram Bot + Backend API :33333
- **技術棧：** Python / FastAPI / kiro-cli / EventBus / SQLite

## 團隊成員

| Agent | 角色 | 狀態 |
|-------|------|------|
| admin-agent | 👑 Admin | idle |
| leader-agent | 🧠 Leader | active |
| ai-dev-agent | 🤖 AI Dev | 執行中 |
| coder-agent | 💻 Coder | 執行中 |
| qa-agent | 🧪 QA | 執行中 |

## 已完成里程碑

### 2026-06-17：平台初始化
- 建立全部核心模組（ark_team_core / backend / tg_ui / a2a）
- 5 個 Agent + 55 個 Skills 就緒
- start.py 一鍵啟動全平台

### 2026-06-18：日報 + 分析
- 產出日報（MD + HTML）並 TG 傳送
- 完成 ai-team-agent 全面分析，產出 15 項優化清單

### 2026-06-19：優化計畫派工執行
- ✅ Week 1（#1-3）：Agent Queue + 可配置超時 + A2A Router 接入
- ✅ Week 2（#4-6）：Token 精算 + FeedbackLoop + Agent Profiles
- 🟡 Week 3（#7-10）：SharedMemory + TG通知分級 + AsyncDB + Graceful Shutdown（進行中）
- 🟡 Week 5（#11-14）：Metrics + Marker + Scheduler追蹤 + 整合測試（進行中）
- 🟡 額外：TG 回覆經 LLM 摘要整理（進行中）

## 關鍵文件

| 文件 | 路徑 |
|------|------|
| 優化計畫 | docs/plans/ai-team-agent-optimization-plan.md |
| Prompt 優化 One Pager | docs/one-pagers/prompt-assembly-optimization.md |
| 平台設計文件 | docs/ark-platform-design.md |
| 日報 | docs/daily-report-2026-06-18.md |

## 使用者偏好

- 回覆語言：繁體中文
- 風格：結論先行、精簡
- TG 通知：只要結果摘要，不要過程
- 派工模式：我決定做法 → 背景執行 → TG 傳結果

## 待辦

- [ ] 確認 Week 3 + Week 5 任務完成
- [ ] 驗收所有優化項目
- [ ] 更新 MEMORY 最終結果

## 備註

- TG chat_id: 937896656
- Bot token env: TELEGRAM_BOT_TOKEN
- 平台 port: 33333
- 派工 API: POST /api/issues → PATCH /api/issues/{id}/assign

---
title: "Ark Agent Platform 執行計畫"
type: plan
version: "1.0"
status: draft
language: zh-TW
author: paddyyang
created: 2026-06-17
updated: 2026-06-17
related_design: "docs/ark-platform-design.md"
related_specs:
  - "docs/specs/ark-telegram-ui-spec.md"
  - "docs/specs/ark-backend-tool-spec.md"
---

# Ark Agent Platform — 執行計畫

## 1. 摘要

將現有 `ark-agent-team-builder`（282 行最小 daemon）升級為完整的 AI Agent 管理平台，包含 Backend API（FastAPI + PostgreSQL + Event Bus）和 Telegram Rich UI（11 指令 + 通知 + InlineKeyboard），預計 **6 週**交付 MVP，支援 5 人 AI 團隊的完整派工、監控、費用追蹤與審計功能。

---

## 2. 里程碑（Milestones）

### Phase 1: Backend 基礎建設（Week 1）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| DB schema 設計 + migration | coder-agent | 4h | 無 | 6 張表建立成功，migration 可重複執行 |
| EventBus 實作 | ai-dev-agent | 4h | 無 | 14 種事件 emit/subscribe 通過單元測試 |
| FastAPI router + middleware | coder-agent | 4h | DB | health endpoint 回 200 |
| Agents CRUD API | coder-agent | 4h | router | POST/GET/DELETE agents 通過 |
| Issues lifecycle API | coder-agent | 6h | router + DB | create/assign/complete/fail 全通過 |
| WebSocket endpoint | ai-dev-agent | 4h | EventBus | client 連線後收到即時事件 |
| 整合測試 | qa-agent | 4h | 全部 | 10 個 API test cases 通過 |

**Phase 1 交付物**：
- [ ] `src/backend/db/models.py` — 6 張表 ORM
- [ ] `src/backend/db/migrations/001_init.sql` — DDL
- [ ] `src/backend/events/bus.py` — EventBus
- [ ] `src/backend/events/types.py` — 14 種 EventType
- [ ] `src/backend/api/router.py` — FastAPI app
- [ ] `src/backend/api/agents.py` — Agent CRUD
- [ ] `src/backend/api/issues.py` — Issue lifecycle
- [ ] `src/backend/api/ws.py` — WebSocket push
- [ ] `tests/test_api.py` — 整合測試

---

### Phase 2: Backend 服務完整化（Week 2）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| Dashboard stats + trends API | coder-agent | 4h | DB | 回傳正確聚合數據 |
| Session Inspector API | coder-agent | 6h | DB | session list + turn detail 正確 |
| Cost Tracker service | ai-dev-agent | 4h | EventBus + DB | agent.output 後自動記錄費用 |
| Audit Logger service | ai-dev-agent | 4h | EventBus + DB | 所有 mutation 自動記錄 |
| Health Monitor | coder-agent | 4h | daemon + EventBus | 離線 agent 自動重啟 + 發事件 |
| Queue Manager API | coder-agent | 4h | DB | priority CRUD + batch ops |
| Budget warning logic | ai-dev-agent | 2h | Cost Tracker | 超閾值自動 emit 事件 |
| Phase 2 測試 | qa-agent | 4h | 全部 | Admin API 15 端點全通過 |

**Phase 2 交付物**：
- [ ] `src/backend/api/admin.py` — Admin 5 域 API
- [ ] `src/backend/services/cost_tracker.py`
- [ ] `src/backend/services/audit_logger.py`
- [ ] `src/backend/services/health_monitor.py`
- [ ] `tests/test_admin.py` — Admin API 測試
- [ ] `tests/test_services.py` — Services 測試

---

### Phase 3: Telegram UI 基礎（Week 3）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| Bot 骨架 + /start /status /agents | coder-agent | 4h | Backend API | Bot 啟動、3 指令回覆正確 |
| /board /costs /queue 指令 | coder-agent | 4h | Admin API | 查詢類指令回傳格式化卡片 |
| Formatters（5 種卡片模板） | ai-dev-agent | 4h | 無 | status/completed/board/cost/blocker 模板正確 |
| /assign 流程 + InlineKeyboard | coder-agent | 6h | Issues API | 完整派工 flow 可操作 |
| 自然語言路由（@mention） | ai-dev-agent | 4h | 無 | @agent_name 正確路由 |
| TG 整合測試 | qa-agent | 4h | 全部 | 11 指令全部可用 |

**Phase 3 交付物**：
- [ ] `src/telegram/bot.py` — 入口
- [ ] `src/telegram/handlers/commands.py` — 11 指令
- [ ] `src/telegram/handlers/messages.py` — 自然語言路由
- [ ] `src/telegram/handlers/callbacks.py` — InlineKeyboard
- [ ] `src/telegram/formatters.py` — 5 種卡片模板
- [ ] `src/telegram/keyboards.py` — 按鈕工廠

---

### Phase 4: Telegram 互動 + 通知（Week 4）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| NotificationService（EventBus → TG） | ai-dev-agent | 6h | EventBus | 6 種事件正確推送 |
| 任務完成/失敗/blocker 通知 | coder-agent | 4h | Notification | 即時收到格式化通知 |
| Progress 更新器（edit_message） | coder-agent | 4h | 無 | 進度條即時刷新 |
| Group Topics 路由 | ai-dev-agent | 4h | TG API | 每 agent 回覆進入正確 topic |
| 審批 flow + /stop /retry /logs | coder-agent | 4h | Issues API | 操作指令全通過 |
| 每日摘要排程 | coder-agent | 2h | Scheduler | 21:00 自動推送 |
| Phase 4 測試 | qa-agent | 4h | 全部 | 通知延遲 < 5s |

**Phase 4 交付物**：
- [ ] `src/telegram/notifications.py` — 事件推送
- [ ] `src/telegram/progress.py` — 進度更新
- [ ] 6 種通知模板完整實作
- [ ] Group Topics 路由正確

---

### Phase 5: 端到端整合（Week 5）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| process.py → EventBus 串接 | ai-dev-agent | 4h | EventBus | spawn 完成自動 emit |
| TG commands → Backend API 串接 | coder-agent | 4h | 全部 | 指令經 API 操作 DB |
| WebSocket → TG 通知完整流程 | ai-dev-agent | 4h | WS + Notification | event 從 daemon 到 TG 完整鏈路 |
| start.py 統一入口重構 | coder-agent | 4h | 全部 | 單指令啟動全平台 |
| 端到端整合測試 | qa-agent | 8h | 全部 | 派工 → 執行 → 通知 完整 flow |

**Phase 5 交付物**：
- [ ] `ark_team_core/` 升級版（+event emit）
- [ ] `start.py` 統一入口
- [ ] `tests/test_integration.py` — E2E 測試
- [ ] 完整派工流程可 demo

---

### Phase 6: 打磨 + 部署（Week 6）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| RBAC 權限控制 | ai-dev-agent | 4h | API | admin/member/viewer 三級生效 |
| Docker Compose 生產配置 | coder-agent | 4h | 全部 | `docker compose up` 一鍵啟動 |
| E2E 自動化測試 | qa-agent | 6h | 全部 | CI 綠燈 |
| 效能壓測 | qa-agent | 4h | 全部 | 50 agents / P95 < 200ms |
| 文件更新 | pm-agent | 4h | 全部 | README + API docs + CHANGELOG |
| 安全性掃描 | qa-agent | 2h | 全部 | 0 critical issues |

**Phase 6 交付物**：
- [ ] `src/backend/api/auth.py` — RBAC
- [ ] `docker-compose.prod.yml`
- [ ] `e2e/` — Playwright 測試
- [ ] 壓測報告
- [ ] `README.md` + `CHANGELOG.md` 更新

---

## 3. 風險管理（Risk Management）

| 風險 | 機率 | 影響 | 緩解策略 | 觸發條件 |
|------|------|------|----------|----------|
| kiro-cli 版本不相容 | M | H | Pin 版本 + 啟動前 version check | spawn 失敗率 > 20% |
| LLM 費用失控 | H | H | cost_guard + budget warning + 自動暫停 | 日費超過設定值 |
| SQLite 併發瓶頸 | L | M | 開發用 SQLite、生產切 PostgreSQL | 寫入衝突 > 5/min |
| Telegram API 限流 | M | M | 訊息佇列 + 500ms 節流 | 429 錯誤 > 3 次/min |
| Event Bus 記憶體洩漏 | L | H | Queue maxsize=10000 + 定期 drain | 記憶體 > 1GB |
| 整合階段延遲 | M | M | Phase 5 預留 buffer + 可砍 Group Topics | W5 開始仍有 > 3 blocker |
| Agent 回應品質不穩 | M | L | 重試機制 + fallback 到備選模型 | 連續失敗 > 3 次 |

---

## 4. 驗證標準（Verification Criteria）

| 類別 | 指標 | 目標 | 驗證方式 |
|------|------|------|----------|
| 單元測試 | 覆蓋率 | > 80% | `pytest --cov` |
| API 測試 | 端點覆蓋 | 15/15 端點通過 | `pytest tests/test_api.py` |
| 整合測試 | 派工 E2E | TG 發訊 → Agent 完成 → TG 通知 < 3 min | 手動 + 自動 |
| 效能 | P95 延遲 | < 200ms（API）/ < 5s（通知） | k6 壓測 |
| 安全性 | 漏洞掃描 | 0 critical | bandit + safety |
| 穩定性 | 持續運行 | 24h 無 crash | daemon 持續運行監控 |
| 費用準確度 | 追蹤誤差 | < 10% vs 實際帳單 | 月底比對 |

---

## 5. 回滾計畫（Rollback Plan）

| 觸發條件 | 回滾步驟 | 預估時間 | 負責人 |
|----------|----------|----------|--------|
| API 啟動失敗 | 還原 start.py 到舊版（純 daemon） | 2 min | admin-agent |
| DB migration 失敗 | `alembic downgrade -1` | 1 min | coder-agent |
| TG Bot 異常 | 停用 TG adapter，HTTP API 仍可用 | 即時 | admin-agent |
| 費用暴衝 | cost_guard 自動暫停所有 agent | 即時（自動） | system |
| 整合完全失敗 | 回退到 Phase 0（純 daemon + 簡易 TG） | 5 min | admin-agent |

---

## 6. 依賴與前置條件

### 外部依賴

| 依賴 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | Runtime |
| PostgreSQL | 17（生產）/ SQLite（開發） | 持久化 |
| kiro-cli | 2.7+ | Agent 引擎 |
| python-telegram-bot | 22+ | Telegram API |
| FastAPI | 0.110+ | REST API |
| uvicorn | 0.27+ | ASGI server |
| SQLAlchemy | 2.0+ | ORM（可選 aiosqlite） |
| APScheduler | 3.10+ | 排程 |

### 環境需求

- Telegram Bot Token（@BotFather）
- 網路存取（Telegram API + LLM API）
- 磁碟 > 1GB（日誌 + DB）
- RAM > 2GB（5 agents 併發）

### 人力需求

| 角色 | 職責 | 負荷 |
|------|------|------|
| pm-agent (leader) | 需求釐清、驗收、每日 standup | 20% |
| ai-dev-agent | 架構設計、Event Bus、通知、AI 整合 | 100% W1-5 |
| coder-agent | API 開發、TG 指令、CRUD、整合 | 100% W1-6 |
| qa-agent | 測試、壓測、安全掃描 | 50% W1-4, 100% W5-6 |
| admin-agent | 部署、監控、回滾 | 20% |

---

## 7. 溝通計畫

| 事件 | 通知對象 | 管道 | 頻率 |
|------|----------|------|------|
| 每日進度 | 全團隊 | TG Group /Daily Report topic | 每日 21:00 |
| Phase 完成 | pm-agent + admin | TG 私訊 | 每週 |
| Blocker 升級 | pm-agent | TG 即時通知 | 即時 |
| 風險觸發 | admin-agent | TG ⚠️ Alerts topic | 即時 |
| MVP Demo | 全員 | 螢幕分享 | W3 + W6 |
| 上線通知 | 全員 | TG 公告 | 一次 |

---

## 8. 成功標準

| 指標 | MVP 目標 | 衡量 |
|------|---------|------|
| 派工到完成 | TG 發訊 → 收到結果 < 3 min（簡單任務） | E2E 計時 |
| 指令回應 | TG 指令 → 回覆 < 2s | 日誌 |
| 通知即時性 | 事件 → TG 推送 < 5s | Event timestamp diff |
| 費用透明度 | 每次 spawn 都有費用記錄 | DB record count = spawn count |
| 穩定性 | 24h 無人值守不 crash | uptime 監控 |
| 使用者滿意 | 能用 TG 完成 80% 的日常操作 | 人工驗證 |

---

## 9. 開放問題

| # | 問題 | 決策時限 | 影響 |
|---|------|---------|------|
| 1 | SQLite vs PostgreSQL for MVP？ | W1 D1 | 如果只用 SQLite，Phase 6 壓測可能受限 |
| 2 | Token 計數用估算還是精確計算？ | W2 D1 | 精確需 tiktoken，估算用 chars/4 |
| 3 | Group Topics 是否列入 MVP？ | W3 結束 | 可延後到 v1.1 |
| 4 | 是否整合 Multica Cloud API？ | W5 | 整合可共享 Web Dashboard，不整合獨立運作 |

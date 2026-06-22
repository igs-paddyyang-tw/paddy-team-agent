---
title: "AI Team Agent 優化項目清單"
type: plan
status: draft
author: pm-agent
created: 2026-06-19
updated: 2026-06-19
---

# AI Team Agent 優化項目清單

## 🔴 高優先（Week 1-2）

### 1. Agent 任務佇列（取代丟棄）

- **問題**：Agent 忙碌時新任務直接 return None，任務遺失
- **改法**：每個 AgentProcess 加入 `asyncio.Queue`，忙碌時排隊等待
- **檔案**：`src/ark_team_core/process.py`
- **大小**：S

### 2. 可配置超時（對齊 hang_detector）

- **問題**：process.py 硬編碼 300s，但 team.yaml 設了 60 min
- **改法**：從 config 讀取 `hang_detector.timeout_minutes`，傳入 `asyncio.wait_for`
- **檔案**：`src/ark_team_core/process.py`、`config.py`
- **大小**：XS

### 3. 接入 A2A Router

- **問題**：`src/a2a/` 五個模組已寫好但 `start.py` 從未使用
- **改法**：在 `start.py` 初始化 `A2ARouter(graph, memory, discovery, spawn_fn)`，派工改走 `router.dispatch(handoff)`
- **檔案**：`start.py`
- **大小**：M

### 4. Token 消耗精算

- **問題**：目前用 `len(output) // 4` 估算，完全忽略 input token
- **改法**：kiro-cli 加 `--json` flag 或從 stderr 解析 token usage，回填 DB
- **檔案**：`src/ark_team_core/process.py`、`start.py` `_on_agent_output`
- **大小**：S

### 5. FeedbackLoop 整合

- **問題**：任務失敗直接標 failed，無自動修復
- **改法**：失敗時檢查 `task.loop_back`，有值則進入 `FeedbackLoop.run()`
- **檔案**：`src/a2a/router.py`、`start.py`
- **大小**：S

---

## 🟡 中優先（Week 3-4）

### 6. Agent Profiles 填充

- **問題**：`knowledge/shared/agent_profiles/` 是空的，Discovery 無法匹配
- **改法**：為 5 個 agent 各建立 YAML profile（skills、capacity、role）
- **檔案**：`knowledge/shared/agent_profiles/*.yaml`
- **大小**：S

### 7. SharedMemory 可達性

- **問題**：Agent 各自有 working_dir，看不到 `knowledge/shared/`
- **改法**：方案 A — symlink；方案 B — spawn 時 `--context` 注入相關任務檔
- **檔案**：`start.py`、agent working_dir
- **大小**：S

### 8. TG 通知分級

- **問題**：所有 output 都推 TG，長文被截斷，雜訊多
- **改法**：只推「完成摘要」（≤200 字）+ 失敗/blocker 通知，完整結果存 DB 供查詢
- **檔案**：`start.py` `_tg_reply`、`src/tg_ui/notifications.py`
- **大小**：S

### 9. Async DB

- **問題**：`sqlite3.Connection` 是同步，在 async handler 中阻塞 event loop
- **改法**：改用 `aiosqlite`（dev）或 `asyncpg`（prod），包一層 async wrapper
- **檔案**：`src/backend/db/database.py`、`models.py`
- **大小**：M

### 10. Graceful Shutdown

- **問題**：關機直接 kill，進行中任務遺失
- **改法**：設 `_shutting_down` flag，等 current task 完成 or 存入 pending queue 再退出
- **檔案**：`start.py`、`src/ark_team_core/process.py`
- **大小**：S

---

## 🟢 低優先（Week 5+）

### 11. /metrics Endpoint

- **改法**：加 Prometheus 格式的 `/metrics`（active agents、task count、token usage）
- **大小**：S

### 12. Agent Output 結構化 Marker

- **改法**：Agent 回覆加 `[DONE]`、`[ARTIFACT:path]`、`[PROGRESS:3/5]` marker
- **大小**：S（改 agent SOUL.md + progress_parser）

### 13. Scheduler 結果追蹤

- **改法**：排程任務完成後 emit `TASK_COMPLETED` event，串入 EventBus
- **大小**：XS

### 14. 整合測試

- **改法**：補 EventBus、TaskGraph、A2ARouter 的 pytest 測試
- **大小**：M

### 15. Prompt 組裝優化（跨專案）

- **改法**：參考 `docs/one-pagers/prompt-assembly-optimization.md`，分 5 階段執行
- **大小**：L（獨立子計畫）

---

## 執行總覽

| 週次 | 項目 | 負責 Agent |
|------|------|-----------|
| W1 | #1 Agent Queue + #2 可配置超時 | coder-agent |
| W1 | #3 接入 A2A Router | ai-dev-agent |
| W2 | #4 Token 精算 + #5 FeedbackLoop | coder-agent |
| W2 | #6 Agent Profiles | pm-agent |
| W3 | #7 SharedMemory + #8 TG 通知分級 | coder-agent |
| W3 | #9 Async DB | coder-agent |
| W4 | #10 Graceful Shutdown + #14 測試 | qa-agent |
| W5+ | #11-13, #15 | 依優先度排入 |

---

*產出：pm-agent — 2026-06-19*

---
title: "A2A 協作機制 執行計畫"
type: plan
version: "1.0"
status: draft
language: zh-TW
author: paddyyang
created: 2026-06-18
updated: 2026-06-18
related_design: "docs/designs/a2a-collaboration-design.md"
related_spec: "docs/specs/a2a-collaboration-spec.md"
---

# A2A 協作機制 — 執行計畫

## 1. 摘要

為 ai-team-agent 加入 A2A 協作層（~280 行 Python），讓 5 個 agent 能結構化交接、依賴排序、自動修復迴圈、共享 context。預計 **3 週（15 天）** 完成，分 3 Phase。

---

## 2. 里程碑

### Phase 1: 協議 + 進度（Week 1）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| TaskHandoff dataclass | ai-dev-agent | 2h | 無 | import 成功 + 序列化/反序列化 |
| Progress Parser | coder-agent | 2h | 無 | 解析 5 種標記 + 單元測試 |
| process.py 整合 Progress | coder-agent | 2h | Parser | stdout 含 [PROGRESS] → emit event |
| TG 進度條接 PROGRESS 事件 | coder-agent | 2h | EventBus | TG 訊息即時更新步驟 |
| Agent SOUL.md 加入格式指引 | pm-agent | 1h | 協議定義 | 5 個 agent 都有 |
| Phase 1 測試 | qa-agent | 3h | 全部 | agent 輸出 [DONE] → TG 收到 |

**Phase 1 交付物**：
- [ ] `src/a2a/protocol.py` — TaskHandoff + Progress 資料結構
- [ ] `src/a2a/progress_parser.py` — 5 種標記解析
- [ ] `src/ark_team_core/process.py` — +progress parsing
- [ ] `agents/*/. kiro/steering/SOUL.md` — +格式指引

---

### Phase 2: 依賴圖 + 共享記憶（Week 2）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| TaskGraph（DAG）實作 | ai-dev-agent | 4h | protocol | add/ready/complete/unlock 全通過 |
| Shared Memory（檔案系統） | coder-agent | 3h | 無 | write_task/get_context/update 正常 |
| Agent Discovery（能力匹配） | ai-dev-agent | 2h | 無 | 根據 skills 自動選 agent |
| A2A Router（整合） | coder-agent | 4h | Graph + SM + Discovery | dispatch → spawn 完整流程 |
| daemon.py 注入 Router | coder-agent | 2h | Router | start.py 啟動時初始化 |
| Phase 2 測試 | qa-agent | 3h | 全部 | task A → B → C 依賴正確執行 |

**Phase 2 交付物**：
- [ ] `src/a2a/graph.py` — TaskGraph DAG
- [ ] `src/a2a/shared_memory.py` — 檔案系統共享記憶
- [ ] `src/a2a/discovery.py` — Agent 能力匹配
- [ ] `src/a2a/router.py` — A2A Router
- [ ] `knowledge/shared/` — 目錄結構
- [ ] `knowledge/shared/agent_profiles/*.yaml` — 5 個 agent 能力檔

---

### Phase 3: Feedback Loop + 整合（Week 3）

| 任務 | 負責人 | 預估工時 | 依賴 | 驗收條件 |
|------|--------|----------|------|----------|
| FeedbackLoop 實作 | ai-dev-agent | 4h | Router | coder fix → qa retest → max 3 |
| EventBus 新增 A2A 事件 | coder-agent | 2h | protocol | handoff/progress/loop 事件 |
| TG 通知整合 | coder-agent | 2h | Events | blocker → TG / loop 結果 → TG |
| Leader prompt 升級 | ai-dev-agent | 2h | protocol | pm-agent 輸出 TaskHandoff 格式 |
| E2E 測試：完整 A2A 流程 | qa-agent | 4h | 全部 | 派工 → 拆解 → 依賴 → 完成 |
| 文件更新 | pm-agent | 2h | 全部 | README + QUICKSTART 更新 |

**Phase 3 交付物**：
- [ ] `src/a2a/feedback_loop.py`
- [ ] EventBus 新增 4 種事件
- [ ] E2E 測試通過（完整 A2A 流程）
- [ ] 文件更新

---

## 3. 風險管理

| 風險 | 機率 | 影響 | 緩解策略 | 觸發條件 |
|------|------|------|----------|----------|
| Agent 不遵守 PROGRESS 格式 | H | M | SOUL.md 多給範例 + fallback（無標記時用 timer） | >50% 回應無標記 |
| Feedback Loop token 爆掉 | M | H | max_iterations=3 + context 只帶摘要 | 單 loop >$5 |
| 依賴圖 cycle | L | H | add_task 時 cycle detection | graph.add 拋例外 |
| Shared Memory 讀寫時序 | L | M | 每 task 獨立檔案 + atomic rename | 檔案損壞 |
| Leader 拆解品質差 | M | H | 提供範例 + structured output prompt | 下游 agent 頻繁 BLOCKER |

---

## 4. 驗證標準

| 類別 | 指標 | 目標 | 驗證方式 |
|------|------|------|----------|
| 協議遵從 | Agent 輸出含 PROGRESS | >80% sessions | grep log |
| Token 節省 | 後續 agent context 長度 | 比無 shared memory 減少 >40% | 比對 token count |
| 依賴正確 | 依賴未完成不 spawn | 0 次違規 | E2E 測試 |
| Feedback Loop | bug 自動修復率 | >60%（3 輪內修復） | qa 結果統計 |
| 派工延遲 | handoff → spawn | < 2s | 日誌計時 |

---

## 5. 回滾計畫

| 觸發條件 | 回滾步驟 | 預估時間 |
|----------|----------|----------|
| A2A Router crash | 繞過 router，直接 spawn（回到舊模式） | 即時 |
| PROGRESS 解析錯誤 | 關閉 parser，stdout 原樣回傳 | 1 min |
| Shared Memory 損壞 | 清空 knowledge/shared/tasks/，重新開始 | 1 min |
| Feedback Loop 爆 token | 設 max_iterations=0 停用 | 即時 |

---

## 6. 依賴與前置條件

### 技術依賴

| 項目 | 版本 | 用途 |
|------|------|------|
| 現有 EventBus | — | 事件分發 |
| 現有 process.py | — | spawn + stdout 讀取 |
| 現有 knowledge/ | — | 共享記憶目錄 |
| 無新套件 | — | 純 Python stdlib + 現有依賴 |

### 前置條件

- Phase 1-6（Backend + TG）已完成 ✅
- 5 個 agent 可正常 spawn ✅
- EventBus 可 emit/subscribe ✅

---

## 7. 溝通計畫

| 事件 | 管道 | 頻率 |
|------|------|------|
| 每日進度 | TG /status | 每日 |
| Phase 完成 Demo | TG 派工測試 | 每週 |
| Blocker | TG 即時 | 即時 |

---

## 8. 成功標準

```
✅ 派工「建立 Todo App」→ leader 拆為 3 task（依賴正確）
✅ ai-dev 完成 → coder 自動啟動（帶入 ai-dev 的 artifact）
✅ coder 完成 → qa 自動啟動
✅ qa 失敗 → coder 自動修復 → qa 重測 → 通過
✅ 全程 TG 有進度更新（[PROGRESS] 標記）
✅ knowledge/shared/tasks/ 有完整記錄
✅ 總 token 比無 A2A 時減少 >30%
```

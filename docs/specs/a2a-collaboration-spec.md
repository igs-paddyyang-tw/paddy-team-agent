---
title: "A2A 協作機制規格書"
status: implemented
type: spec
version: "1.0"
language: zh-TW
author: paddyyang
created: 2026-06-18
updated: 2026-06-18
---

# A2A 協作機制 — 規格書

## 1. 問題陳述

現有 ai-team-agent 的 5 個 agent 各自獨立執行，缺乏：
- **標準化交接**：leader 派工靠自然語言，格式不一致，接收端常誤解
- **進度回報**：agent 執行 30-300 秒完全黑箱，人類無法判斷是卡住還是正常
- **Context 傳遞**：coder 完成後 qa 要重新理解，浪費 50% token 在重複 context
- **任務依賴**：qa 被派工但 coder 還沒寫完，浪費一次 spawn
- **自動修復迴圈**：qa 報 bug 需人類手動轉給 coder，無法自動 fix → retest

**結果**：5 個 agent 是「5 個獨立工人」而非「1 個協作團隊」。

---

## 2. 目標與非目標

### 目標

| # | 目標 | 衡量指標 |
|---|------|---------|
| G1 | 標準化 Task Handoff 協議 | 100% 跨 agent 任務使用結構化格式 |
| G2 | 即時進度回報 | agent 執行中每 30 秒有進度更新 |
| G3 | 共享記憶體 | 後續 agent 不需重複 context（token 節省 >40%） |
| G4 | 任務依賴圖 | 依賴未完成的任務不會被 spawn |
| G5 | 自動 Fix-Retest 迴圈 | qa 報 bug → coder 修 → qa 重測，最多 3 輪 |
| G6 | Agent 能力自動匹配 | leader 不需硬編碼「誰做什麼」 |

### 非目標

- 不重寫 agent runtime（保持 kiro-cli spawn）
- 不引入新的 LLM provider
- 不做跨機器分散式（保持單機）
- 不做 agent 自主對話（仍由 leader 或人類觸發）

---

## 3. 核心設計

### 3.1 Task Handoff Protocol

```python
@dataclass
class TaskHandoff:
    """A2A 任務交接標準格式。"""
    task_id: str                    # 唯一任務 ID
    from_agent: str                 # 發起者
    to_agent: str                   # 接收者（或 "auto" 自動匹配）
    title: str                      # 一行摘要
    context: str                    # 背景（≤500 字）
    input_artifacts: list[str]      # 輸入檔案路徑
    deliverables: list[str]         # 期望產出
    acceptance_criteria: str        # 驗收條件
    priority: int                   # 1-4
    depends_on: list[str]           # 依賴的 task_id
    loop_back: str | None           # 完成後回傳給誰（feedback loop）
    max_iterations: int             # 最大迴圈次數
```

### 3.2 Progress Streaming Protocol

Agent 在 stdout 中輸出結構化進度標記：

```
[PROGRESS] step=1/4 msg=分析需求中
[PROGRESS] step=2/4 msg=建立 API 端點
[ARTIFACT] path=src/api.py msg=API 建立完成
[BLOCKER] need=db_schema msg=需要 user_profiles 表定義
[PROGRESS] step=3/4 msg=撰寫測試
[DONE] summary=完成 5 個 API 端點 artifacts=src/api.py,tests/test_api.py
[FAIL] reason=timeout msg=外部 API 無回應
```

### 3.3 Shared Memory

```
knowledge/shared/
├── tasks/
│   └── {task_id}.md           # 任務狀態文件
├── decisions/
│   └── {topic}.md             # 跨 agent 決策記錄
├── artifacts/
│   └── {file}                 # 共享產出物
└── agent_profiles/
    └── {agent_id}.yaml        # 能力註冊
```

任務狀態文件格式：
```markdown
---
task_id: task_42
status: implemented
assigned_to: coder-agent
depends_on: [task_41]
created_by: leader-agent
---
# 建立 REST API
## Context
需求來自 task_41 的設計文件...
## Deliverables
- [ ] src/api.py
- [ ] tests/test_api.py
## Notes
（agent 可追加筆記）
```

### 3.4 Dependency Graph

```python
class TaskGraph:
    """DAG 任務依賴圖。"""

    def add_task(self, task: TaskHandoff) -> None: ...

    def get_ready_tasks(self) -> list[TaskHandoff]:
        """回傳所有依賴已完成的待執行任務。"""

    def mark_complete(self, task_id: str, output: str) -> list[TaskHandoff]:
        """標記完成，回傳被解鎖的下游任務。"""

    def mark_failed(self, task_id: str, reason: str) -> None:
        """標記失敗，阻塞所有下游。"""
```

### 3.5 Feedback Loop

```python
class FeedbackLoop:
    """自動 fix-retest 迴圈。"""

    async def run(self, task: TaskHandoff, executor: str, reviewer: str, max_iter: int = 3):
        for i in range(max_iter):
            result = await spawn(executor, task)
            review = await spawn(reviewer, f"Review: {result}")
            if review.passed:
                return result
            task.context = f"第 {i+1} 次修正，問題：{review.issues}"
        raise MaxIterationsExceeded()
```

### 3.6 Agent Discovery

```yaml
# knowledge/shared/agent_profiles/coder-agent.yaml
agent_id: coder-agent
skills: [python, typescript, fastapi, express, postgresql, docker]
role: worker
avg_completion_s: 45
current_load: 0.2    # 動態更新
max_concurrent: 1
```

---

## 4. 模組結構

```
src/a2a/
├── __init__.py
├── protocol.py          # TaskHandoff + Progress 資料結構
├── graph.py             # TaskGraph（DAG）
├── shared_memory.py     # 讀寫 knowledge/shared/
├── discovery.py         # Agent 能力匹配
├── feedback_loop.py     # Fix-Retest 迴圈
├── progress_parser.py   # 解析 stdout 進度標記
└── router.py            # A2A 路由（整合以上模組）
```

---

## 5. 與現有系統整合

| 現有模組 | 整合方式 |
|----------|---------|
| `process.py` | `send()` 回傳值加入 progress parsing |
| `daemon.py` | 注入 TaskGraph，spawn 前檢查依賴 |
| `start.py` | 初始化 A2A router + shared memory |
| `EventBus` | 新增 `task.handoff` / `task.progress` / `task.loop_iteration` 事件 |
| `tg_ui/notifications.py` | 訂閱新事件 → TG 推送 |
| `tg_ui/progress.py` | 用 PROGRESS 標記更新進度條 |
| Agent SOUL.md | 加入輸出格式指引（PROGRESS/DONE/BLOCKER） |

---

## 6. 非功能性需求

| 指標 | 目標 |
|------|------|
| Handoff 延遲 | < 1s（寫入 shared memory + 觸發下游） |
| Progress 解析 | < 10ms per line |
| Shared Memory I/O | 檔案系統（無 DB 依賴） |
| 依賴圖 | 支撐 50 concurrent tasks |
| Feedback Loop | max 3 iterations（防止 token 爆掉） |
| 記憶體 | TaskGraph < 10MB |

---

## 7. 驗收條件

| 機制 | Pass 條件 |
|------|-----------|
| Task Handoff | leader 派工 → coder 收到結構化 TaskHandoff → 回覆含 deliverables |
| Progress | agent stdout 含 `[PROGRESS]` → TG 進度條即時更新 |
| Shared Memory | coder 寫 artifact → qa 讀取不需重新 context |
| Dependency | task B depends_on A → A 未完成時 B 不被 spawn |
| Feedback Loop | qa 報 3 個 bug → coder 修 → qa 重測 → 最終通過 |
| Discovery | 新增 agent → leader 自動發現並派工 |

---

## 8. 開放問題

| # | 問題 | 決策時限 |
|---|------|---------|
| 1 | Shared Memory 用檔案系統 vs SQLite？ | W1 開始前 |
| 2 | SOUL.md 改多少？（太多指引會降低創意） | W1 |
| 3 | Feedback Loop 超過 3 次怎麼辦？（通知人類 or 放棄） | W2 |
| 4 | 是否需要 agent 間直接通訊？（vs 全部經 leader） | W3 |

---
title: "Agent 間溝通協議"
type: system
tags: [communication, protocol, a2a]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# Agent 間溝通協議

## 訊息標記格式

| 標記 | 用途 | 範例 |
|------|------|------|
| `[DONE] summary=...` | 任務完成回報 | `[DONE] summary=API 已實作完成，3 個端點` |
| `[PROGRESS] step=N/M msg=...` | 進度回報 | `[PROGRESS] step=2/5 msg=資料庫設計完成` |
| `[ARTIFACT] path=... msg=...` | 產出物通知 | `[ARTIFACT] path=src/api.py msg=新增 3 個端點` |
| `[BLOCKER] need=... msg=...` | 卡關求助 | `[BLOCKER] need=coder-agent msg=需要 API 規格` |
| `[FAIL] reason=... msg=...` | 任務失敗 | `[FAIL] reason=timeout msg=LLM 回應超時` |

## 回報時機

| 情境 | 何時回報 |
|------|---------|
| 收到任務 | 立即確認（不需要標記） |
| 進行中（>2 分鐘） | 每完成一個步驟發 [PROGRESS] |
| 完成 | 發 [DONE]（必要） |
| 卡關 | 立即發 [BLOCKER]（不要等） |
| 失敗 | 發 [FAIL] + 原因 |

## 升級路徑

```
Level 1: Agent 自己解決（retry、換方法）
Level 2: [BLOCKER] → leader-agent 協調其他 Agent 幫忙
Level 3: leader-agent 無法解決 → admin-agent 介入
Level 4: admin-agent 無法解決 → 通知使用者（TG 訊息）
```

## 任務交接格式（TaskHandoff）

```yaml
task_id: "2026-07-08_001_api-design"
from_agent: "leader-agent"
to_agent: "coder-agent"       # "auto" = 自動匹配
title: "設計使用者管理 API"
context: "需要 CRUD + 權限控制..."
acceptance_criteria: "3 個端點 + Swagger 文件 + 測試通過"
priority: 2                    # 1=urgent 2=high 3=normal 4=low
```

## 禁止事項

- ❌ Worker 之間不互相派工（一律透過 leader-agent）
- ❌ 不在沒有 [DONE] 的情況下結束任務
- ❌ 卡關超過 5 分鐘不回報
- ❌ 不重複回報已完成的任務

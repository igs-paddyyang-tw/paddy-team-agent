---
title: "派工規則"
type: concept
tags: [dispatch, task-management, load-balancing, rules]
sources: []
related: [requirements-analysis-sop, acceptance-criteria-template, team-communication]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# 派工規則

PM Agent 將任務分派給團隊成員的四大原則：**能力匹配 → 負載平衡 → 依賴排序 → 逾時處理**。

---

## 1. 能力匹配（Capability Matching）

| 任務類型 | 首選 Agent | 備援 Agent |
|---------|-----------|-----------|
| 程式開發 | dev-agent | — |
| 程式碼審查 | review-agent | dev-agent |
| 測試驗證 | qa-agent | dev-agent |
| 文件撰寫 | doc-agent | leader-agent |
| 架構設計 | dev-agent | leader-agent |

**匹配邏輯**：
1. 根據任務 `tags` 比對 Agent 的 `skills` 清單
2. 計算匹配度分數（完全匹配 1.0、部分匹配 0.5）
3. 分數 ≥ 0.7 才可派工；否則升級為人工指派

## 2. 負載平衡（Load Balancing）

```
負載分數 = 進行中任務數 × 權重
權重 = { Must: 3, Should: 2, Could: 1 }
```

**規則**：
- 同一 Agent 負載分數 ≤ 9（例如最多 3 個 Must 任務）
- 超過閾值時，任務排入等待佇列
- 等待佇列 FIFO，但 Must 優先級可插隊

## 3. 依賴排序（Dependency Ordering）

派工前必須解析任務依賴圖：

| 情境 | 處理方式 |
|------|---------|
| A 依賴 B 的產出 | B 先派工，A 進入 `blocked` 狀態 |
| A、B 互不依賴 | 可並行派工 |
| 循環依賴 | 標記異常，升級給使用者決策 |

**排序演算法**：拓撲排序（Topological Sort），檢測循環後再派工。

## 4. 逾時處理（Timeout Handling）

| 階段 | 時限 | 動作 |
|------|------|------|
| 任務接受 | 派工後 30 秒 | 未回應 → 重新派給備援 |
| 進度回報 | 每 5 分鐘 | 無回報 → 發送 ping |
| 任務完成 | 依估時 ×1.5 | 超時 → 通知 PM + 使用者 |
| 最終期限 | 估時 ×2.0 | 強制回收 + 錯誤報告 |

**逾時升級路徑**：
```
Agent 無回應 → PM 重試 (×1) → 備援 Agent → 通知使用者
```

---

## 派工訊息格式

```json
{
  "task_id": "TASK-001",
  "assigned_to": "dev-agent",
  "priority": "Must",
  "deadline": "2026-07-08T18:00:00+08:00",
  "dependencies": [],
  "acceptance_criteria": "參見 spec",
  "timeout_minutes": 30
}
```

派工完成後，PM 必須在 [[team-communication]] 中發送 `[DISPATCH]` 通知。

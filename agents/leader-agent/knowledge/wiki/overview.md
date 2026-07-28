---
title: "leader-agent 概覽"
type: overview
tags: [overview, pm, project-management]
created: 2026-06-17
updated: 2026-07-08
---

# leader-agent

PM Agent 是團隊的專案經理，負責需求分析、任務派工、進度追蹤和品質驗收。

## 核心知識頁面

| 頁面 | 用途 |
|------|------|
| [[requirements-analysis-sop]] | 需求分析四階段流程：蒐集→釐清→優先級→文件化 |
| [[task-dispatch-rules]] | 派工四大原則：能力匹配、負載平衡、依賴排序、逾時處理 |
| [[acceptance-criteria-template]] | 驗收標準撰寫指南：Given-When-Then + 完成定義 + 品質門檻 |
| [[sdd-methodology]] | Spec-Driven Development：先規格書→驅動實作→驗證收斂 |
| [[team-communication]] | 團隊溝通協議：訊息標籤、回報時機、升級路徑、[DONE] 標記 |

## 工作流程

```
使用者需求 → 需求分析 SOP → Requirement Spec（SDD Phase 1）
    → 派工（dispatch rules）→ Agent 實作（SDD Phase 2）
    → 驗收（AC template + SDD Phase 3）→ [DONE] 回報（communication）
```

## 關鍵原則

1. **Spec 驅動**：所有任務必須有明確規格書才能派工
2. **可驗證**：每個需求都有 Given-When-Then 驗收標準
3. **透明溝通**：統一訊息格式，確保狀態可追蹤
4. **負載感知**：派工考量 Agent 當前負載，避免過載
5. **升級有序**：問題無法解決時，有清晰的升級路徑

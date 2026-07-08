---
title: "Agent 設計模式"
type: guide
tags: [agent, soul, multi-agent, memory, feedback-loop]
created: 2026-07-08
updated: 2026-07-08
status: evergreen
---

# Agent 設計模式

## SOUL 設計原則

SOUL 是 Agent 的人格定義框架，包含四個核心維度：

| 維度 | 說明 | 範例 |
|------|------|------|
| **S**kill（技能） | Agent 擅長什麼 | "精通 Python、熟悉 AWS 架構" |
| **O**utput（輸出） | 回應的格式和風格 | "簡潔技術風、Markdown 格式" |
| **U**nderstanding（理解） | 領域知識範圍 | "遊戲產業競品分析、財務報表" |
| **L**imits（邊界） | 不做什麼、何時拒絕 | "不提供法律建議、超出範圍轉介" |

**設計流程**：
1. 定義目標用戶和使用場景
2. 撰寫 SOUL 四維度描述
3. 編寫 3-5 個對話範例測試人格一致性
4. 迭代調整直到通過 Eval 基準

## 多 Agent 協作

### 協作模式

| 模式 | 架構 | 適用場景 |
|------|------|----------|
| **Orchestrator** | 中央排程 Agent 分派子任務 | 複雜流程、依賴關係多 |
| **Pipeline** | Agent 串接，前一個的輸出是下一個的輸入 | 線性流程（分析→撰寫→審核） |
| **Debate** | 多 Agent 討論後投票/合成 | 決策品質要求高 |
| **Specialist** | 依問題類型路由到專家 Agent | 客服、多領域知識 |

### 通訊設計

- **Message Schema**：統一訊息格式（role, content, metadata）
- **Handoff Protocol**：明確的任務交接條件和上下文傳遞
- **Shared Memory**：使用共享知識庫避免重複檢索
- **Timeout & Fallback**：Agent 無回應時的降級策略

## 記憶管理

### 記憶層次

```
┌─────────────────────────────┐
│ Working Memory（當前對話）    │ ← Context Window
├─────────────────────────────┤
│ Short-term Memory（會話摘要） │ ← Session Store
├─────────────────────────────┤
│ Long-term Memory（持久知識）  │ ← Vector DB / Wiki
└─────────────────────────────┘
```

**策略**：
- **Context Compaction**：對話過長時自動摘要壓縮
- **Selective Recall**：根據當前問題檢索相關歷史片段
- **Entity Memory**：追蹤對話中提到的人、事、物
- **Forget Policy**：過期/低相關資訊定期清理

## Feedback Loop（回饋迴圈）

### 自我改進循環

```
Execute → Evaluate → Learn → Adapt
   ↑                           |
   └───────────────────────────┘
```

1. **Execute**：Agent 執行任務產出結果
2. **Evaluate**：自動評估品質（Eval metrics / 用戶反饋）
3. **Learn**：將成功/失敗案例寫入知識庫
4. **Adapt**：調整 prompt/策略/工具選擇

### 實作方式

- **Reflection**：要求 Agent 在回答後自我評估並修正
- **Tool Feedback**：Tool 執行失敗時自動重試或換策略
- **User Feedback**：收集 👍/👎 訓練 reward model
- **Wiki 沉澱**：定期將對話中的知識整理進知識庫
- **A/B 實驗**：不同策略平行測試，數據驅動迭代

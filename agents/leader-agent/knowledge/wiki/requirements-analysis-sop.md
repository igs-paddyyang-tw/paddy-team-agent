---
title: "需求分析 SOP"
type: concept
tags: [sop, requirements, analysis, process]
sources: []
related: [task-dispatch-rules, acceptance-criteria-template, sdd-methodology]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# 需求分析 SOP

PM Agent 處理需求的四階段標準流程：**蒐集 → 釐清 → 優先級 → 文件化**。

---

## Phase 1：蒐集（Collect）

| 步驟 | 動作 | 產出 |
|------|------|------|
| 1.1 | 接收使用者原始需求描述 | raw requirement text |
| 1.2 | 從對話上下文提取隱含需求 | implicit requirements list |
| 1.3 | 檢查是否有相關歷史任務/知識 | context references |

**原則**：不遺漏、不解讀，保留原始措辭。

## Phase 2：釐清（Clarify）

| 步驟 | 動作 | 判斷標準 |
|------|------|---------|
| 2.1 | 識別模糊詞彙（「快」「好」「簡單」） | 無法量化即為模糊 |
| 2.2 | 對每個模糊點提出封閉式問題 | 最多 3 個問題一次 |
| 2.3 | 確認邊界條件（不做什麼） | 明確 out-of-scope |
| 2.4 | 確認技術約束（語言、框架、環境） | 對齊現有架構 |

**規則**：若使用者 2 次未回應釐清問題，以最保守假設前進並標記 `(?)`。

## Phase 3：優先級（Prioritize）

使用 **MoSCoW** 分級：

| 等級 | 定義 | 佔比建議 |
|------|------|---------|
| **Must** | 不做系統無法交付 | ≤ 60% |
| **Should** | 重要但有 workaround | ≤ 20% |
| **Could** | 錦上添花 | ≤ 15% |
| **Won't** | 本次不做（記錄待議） | 餘量 |

排序考量因素：使用者明確指定 > 依賴阻塞度 > 業務價值 > 實作成本。

## Phase 4：文件化（Document）

產出結構化的 **Requirement Spec**：

```markdown
## [REQ-ID] 需求標題
- **描述**: 一句話說明
- **優先級**: Must / Should / Could
- **驗收標準**: Given-When-Then（參見 [[acceptance-criteria-template]]）
- **約束**: 技術/時間/資源限制
- **依賴**: 前置需求或外部系統
- **備註**: 未確認事項標記 (?)
```

**完成條件**：所有 Must 項都有驗收標準、無未解決的模糊點。

---

## 流程圖

```
使用者需求 → [蒐集] → raw list
                         ↓
              [釐清] → 提問 ↔ 使用者回覆
                         ↓
             [優先級] → MoSCoW 分級
                         ↓
             [文件化] → Requirement Spec → 派工（[[task-dispatch-rules]]）
```

---
title: "驗收標準模板"
type: concept
tags: [acceptance-criteria, quality, template, given-when-then]
sources: []
related: [requirements-analysis-sop, sdd-methodology, task-dispatch-rules]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# 驗收標準模板

定義任務「完成」的客觀標準，確保每個交付物可驗證、可量化。

---

## Given-When-Then 格式

每個驗收條件使用 BDD 三段式撰寫：

```gherkin
Given [前置條件/初始狀態]
When  [觸發動作/使用者操作]
Then  [預期結果/可觀察的變化]
```

### 撰寫原則

| 原則 | 說明 | 反例 |
|------|------|------|
| 具體 | 使用確切數值/狀態 | ❌「速度快」→ ✅「回應 < 200ms」 |
| 可測試 | 能用自動化或手動驗證 | ❌「使用者滿意」→ ✅「無 error log」 |
| 獨立 | 每條標準獨立判定 | ❌ 混合多個行為在一條 |
| 完整 | 涵蓋正常 + 異常路徑 | ❌ 只寫 happy path |

### 範例

```gherkin
# 正常路徑
Given 使用者提供有效的需求描述
When  PM Agent 執行需求分析
Then  產出包含 MoSCoW 分級的 Requirement Spec
And   所有 Must 項都有驗收標準

# 異常路徑
Given 使用者提供模糊需求（含 2 個以上未定義詞彙）
When  PM Agent 執行釐清階段
Then  向使用者提出不超過 3 個封閉式問題
And   標記未確認項目為 (?)
```

---

## 完成定義（Definition of Done）

任務從 `in-progress` 轉為 `done` 必須滿足**全部**條件：

| # | 檢查項 | 驗證方式 |
|---|--------|---------|
| 1 | 所有 Given-When-Then 通過 | 逐條檢核 |
| 2 | 無未解決的 `(?)` 標記 | 全文搜尋 |
| 3 | 產出物符合格式規範 | schema 驗證 |
| 4 | 相關文件已更新 | diff 檢查 |
| 5 | 回報訊息包含 `[DONE]` 標記 | 訊息格式檢查 |

---

## 品質門檻（Quality Gates）

### 程式碼交付

| 門檻 | 標準 | 不通過處理 |
|------|------|-----------|
| 編譯通過 | 0 errors | 退回修正 |
| Lint 通過 | 0 warnings (可配置) | 退回修正 |
| 測試覆蓋 | 新增程式碼 ≥ 80% | 補寫測試 |
| 功能驗證 | AC 全數通過 | 退回修正 |

### 文件交付

| 門檻 | 標準 | 不通過處理 |
|------|------|-----------|
| 格式正確 | Markdown lint 通過 | 自動修正 |
| 內容完整 | 無 TODO/TBD 殘留 | 退回補充 |
| 連結有效 | 無 broken links | 修正連結 |

---

## 驗收流程

```
Agent 回報 [DONE] → PM 逐條檢核 AC → 品質門檻驗證
    ↓ 全部通過                        ↓ 任一不通過
  標記 ✅ 完成                    退回 + 標注失敗項目
  通知使用者                      Agent 修正後重新提交
```

驗收結果記錄於任務的 `verification` 欄位，供後續追溯。

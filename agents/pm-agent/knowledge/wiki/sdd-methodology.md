---
title: "SDD 方法論"
type: concept
tags: [sdd, spec-driven, methodology, development-process]
sources: []
related: [requirements-analysis-sop, acceptance-criteria-template, task-dispatch-rules]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# SDD 方法論（Spec-Driven Development）

**核心理念**：先產規格書 → 驅動實作 → 驗證收斂。規格書是唯一事實來源（Single Source of Truth）。

---

## 三階段循環

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. SPEC    │────→│  2. IMPL    │────→│  3. VERIFY  │
│  產出規格書  │     │  驅動實作    │     │  驗證收斂    │
└─────────────┘     └─────────────┘     └─────────────┘
       ↑                                       │
       └───────────── 不收斂時回修 Spec ────────┘
```

---

## Phase 1：SPEC（規格書產出）

PM Agent 負責產出完整規格書，內容包含：

| 區塊 | 內容 | 必要性 |
|------|------|--------|
| Overview | 一段話描述目標 | 必要 |
| Requirements | MoSCoW 分級需求清單 | 必要 |
| Acceptance Criteria | Given-When-Then 格式 | 必要 |
| Technical Constraints | 語言/框架/環境限制 | 必要 |
| Interface Contract | 輸入/輸出/API 定義 | 視任務 |
| Dependencies | 前置任務與外部依賴 | 視任務 |
| Out of Scope | 明確不做的事項 | 建議 |

**品質標準**：Spec 必須讓 Agent 無需額外提問即可開工。

## Phase 2：IMPL（驅動實作）

實作 Agent 收到 Spec 後的工作流程：

1. **解析 Spec** — 提取所有 AC 作為完成檢查清單
2. **拆解子任務** — 將 Spec 拆為可獨立實作的步驟
3. **逐步實作** — 每完成一步，自行對照 AC
4. **自我驗證** — 全部完成後，逐條確認 AC 通過
5. **回報結果** — 附上驗證結果回報 PM

**禁止事項**：
- ❌ 不可偏離 Spec 範圍自行擴展功能
- ❌ 不可跳過 AC 中的任何一條
- ❌ 不可在未確認的情況下更改 Interface Contract

## Phase 3：VERIFY（驗證收斂）

PM Agent 驗證實作是否與 Spec 收斂：

| 檢查項 | 方法 | 不通過處理 |
|--------|------|-----------|
| AC 全數通過 | 逐條比對 | 退回 + 標注失敗項 |
| 產出符合 Interface | 格式/型別驗證 | 退回修正 |
| 無 Scope Creep | 對比 Spec 範圍 | 移除多餘部分 |
| 品質門檻 | 參見 [[acceptance-criteria-template]] | 退回修正 |

---

## 收斂判定

| 狀態 | 條件 | 動作 |
|------|------|------|
| ✅ 收斂 | AC 100% 通過 + 品質門檻全過 | 標記完成，通知使用者 |
| 🔄 未收斂 | 部分 AC 失敗 | 退回 Agent 修正 |
| ⚠️ Spec 缺陷 | 實作揭露 Spec 矛盾/不完整 | PM 修訂 Spec，重啟循環 |

**最大迭代次數**：同一任務最多 3 輪 IMPL → VERIFY。超過則升級給使用者。

---

## SDD vs 傳統開發

| 面向 | 傳統 | SDD |
|------|------|-----|
| 需求文件 | 事後補寫 | 事前驅動 |
| 驗收標準 | 口頭約定 | Spec 內建 |
| 範圍控制 | 容易蔓延 | Spec 為邊界 |
| 迭代方向 | 修改程式碼 | 修改 Spec → 程式碼跟隨 |
| 完成判定 | 主觀感覺 | AC 客觀通過 |

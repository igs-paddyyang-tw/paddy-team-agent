---
title: "Prompt 組裝流程優化計畫"
type: onepager
status: draft
author: paddyyang
language: zh-TW
created: 2026-06-19
updated: 2026-06-19
---

# Prompt 組裝流程優化計畫

## 問題陳述

每次使用者發送訊息，Hermes Agent 將 6 層 context 組裝成完整 prompt 送 LLM API。目前存在以下瓶頸：

1. **Token 浪費**：System Prompt + Tools 固定佔用大量 token，壓縮對話歷史的可用空間
2. **Memory 硬上限**（2200 字）：高頻互動下舊記憶被迫淘汰，關鍵上下文丟失
3. **Skill 注入粗糙**：匹配不精準時注入無關 Skill，浪費 token
4. **Compaction 品質不穩**：自動壓縮可能丟失關鍵細節，導致後續回覆偏離
5. **工具迴圈成本**：多輪 Tool Call 累積 token 消耗，無上限保護

## 目標

| 目標 | 量化指標 |
|------|---------|
| 降低平均 token 消耗 | -30%（相同任務複雜度下） |
| 提升 Memory 利用率 | 關鍵資訊留存率 ≥ 90% |
| 精準 Skill 觸發 | 誤觸率 < 5%、漏觸率 < 10% |
| Compaction 保真度 | 壓縮後語義覆蓋率 ≥ 95% |
| 工具迴圈成本可控 | 單次回覆 Tool Call ≤ 8 輪 |

## 非目標

- 不改 LLM 模型本身
- 不重寫 System Prompt 核心身份/安全護欄
- 不變更 Tool Call JSON Schema 標準

---

## 方案概要

### Phase 1：Prompt 瘦身（Token 節省）

| 優化項 | 做法 | 預期效果 |
|--------|------|---------|
| System Prompt 分層 | 將固定規則拆為「核心」+「按需載入」，非相關規則不注入 | -15% system token |
| Tool 動態篩選 | 只注入本次可能用到的 Tools（基於意圖分類） | -20% tool token |
| 對話歷史滑動窗口 | 近 5 輪完整 + 更早的用摘要替代 | -25% history token |

### Phase 2：Memory 升級

| 優化項 | 做法 | 預期效果 |
|--------|------|---------|
| 分級記憶 | Core（不刪）/ Active（LRU）/ Archive（壓縮存 wiki） | 關鍵資訊不丟 |
| 語義索引 | Memory 加向量索引，按相關度注入而非全量注入 | 精準度 ↑ |
| 容量擴展 | Core 800 字 + Active 1400 字 + 按需召回 Archive | 有效容量 ×3 |

### Phase 3：Skill 觸發精準化

| 優化項 | 做法 | 預期效果 |
|--------|------|---------|
| 二階段匹配 | 先 keyword → 再 semantic similarity 確認 | 誤觸 ↓ |
| 負樣本訓練 | description 加入「不應觸發」情境 | 區分度 ↑ |
| 觸發日誌 | 記錄每次觸發決策，用於持續調優 | 可追溯 |

### Phase 4：Compaction 改善

| 優化項 | 做法 | 預期效果 |
|--------|------|---------|
| 結構化壓縮 | 保留：決策/結論/程式碼；丟棄：寒暄/重複確認 | 保真度 ↑ |
| 雙重驗證 | 壓縮後比對原文關鍵實體覆蓋率 | 品質保證 |
| 使用者 pin | 允許使用者標記「重要」訊息，壓縮時保留 | 使用者可控 |

### Phase 5：Tool Call 成本控制

| 優化項 | 做法 | 預期效果 |
|--------|------|---------|
| 迴圈上限 | 單次回覆最多 8 輪 Tool Call，超過強制回覆 | 成本封頂 |
| 批次呼叫 | 鼓勵 LLM 一次發多個獨立 Tool Call（parallel） | 輪次 ↓ |
| Token 預算 | 每次對話設 token budget，接近時提示精簡 | 預算可控 |

---

## 架構圖

```
User Message
     ↓
┌─────────────────────────────────────┐
│ Intent Classifier（意圖分類）         │
│  → 決定載入哪些 Tools / Skills       │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ Context Assembler（組裝器）           │
│  ├─ System Prompt（核心 + 按需層）   │
│  ├─ Skills（精準匹配後注入）         │
│  ├─ Memory（語義索引召回）           │
│  ├─ Tools（動態篩選）               │
│  ├─ History（滑動窗口 + 摘要）       │
│  └─ User Message                    │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│ Token Budget Guard                   │
│  → 超預算時觸發壓縮/裁剪            │
└─────────────────────────────────────┘
     ↓
  LLM API Call
     ↓
  Tool Loop（≤ 8 輪）
     ↓
  Final Response → User
```

---

## 風險

| 風險 | 緩解 |
|------|------|
| 動態篩選漏掉必要 Tool | 保留「逃生」機制：LLM 可請求載入額外工具 |
| Memory 語義索引不準 | Fallback：相關度低於閾值時注入全量 |
| Compaction 丟失關鍵資訊 | Pin 機制 + 壓縮前 entity 覆蓋檢查 |
| Skill 二階段匹配增加延遲 | Keyword 階段 < 5ms，只有通過才走 semantic |

---

## 執行計畫

| 階段 | 時程 | 優先級 |
|------|------|--------|
| Phase 1：Prompt 瘦身 | Week 1-2 | 🔴 高 |
| Phase 2：Memory 升級 | Week 2-3 | 🔴 高 |
| Phase 3：Skill 精準化 | Week 3-4 | 🟡 中 |
| Phase 4：Compaction | Week 4-5 | 🟡 中 |
| Phase 5：Tool 成本控制 | Week 5-6 | 🟢 低 |

---

## 成功指標

- [ ] 相同任務 token 消耗下降 30%
- [ ] Memory 關鍵資訊留存率 ≥ 90%（人工抽查 20 組對話）
- [ ] Skill 誤觸率 < 5%（100 筆測試查詢）
- [ ] 單次回覆成本 ≤ $0.05（日常任務）
- [ ] 使用者感知回覆品質不下降（滿意度 ≥ 4/5）

---

## 開放問題

1. Memory 語義索引用什麼 embedding model？（本地 vs API）
2. Compaction 的「關鍵實體」定義標準？
3. Tool 動態篩選的意圖分類器要多細？（粗分 5 類 vs 細分 20 類）
4. 是否需要 A/B 測試框架來驗證優化效果？

---

*One Pager by pm-agent — 2026-06-19*

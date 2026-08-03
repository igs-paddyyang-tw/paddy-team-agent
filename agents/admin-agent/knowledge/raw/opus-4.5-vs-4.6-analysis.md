# Claude Opus 4.5 vs 4.6 差異分析

> 來源：2026-08-02 對話研究整理

## 核心差異摘要

| 維度 | Opus 4.5 | Opus 4.6 | 差距 |
|------|----------|----------|------|
| Context Window | 200K | 1M (beta) | 5x |
| Max Output | 64K | 128K | 2x |
| Thinking 模式 | Extended Thinking | Adaptive Thinking | 架構重構 |
| 多 Agent | Subagent only | Agent Teams + Subagent | 新增 |
| 價格 | $5/$25 per MTok | $5/$25 per MTok | 不變 |

## Benchmark 對比

### 推理能力（差距最大）
- ARC AGI 2：37.6% → 68.8%（+31.2pp）
- GPQA Diamond：87.0% → 91.3%（+4.3pp）
- Humanity's Last Exam：43.4% → 53.1%（+9.7pp）

### Coding（差距小）
- Terminal-Bench 2.0：59.8% → 65.4%（+5.6pp）
- SWE-bench Verified：80.9% → 80.8%（-0.1pp，持平）

### 實用場景
- BrowseComp：67.8% → 84.0%（+16.2pp）
- OSWorld：66.3% → 72.7%（+6.4pp）
- MCP Atlas：62.3% → 59.5%（-2.8pp，退步）

## 4.6 獨有功能

1. **Adaptive Thinking** — effort 參數（low/medium/high/max）取代固定 budget
2. **Context Compaction API** — 伺服器端自動壓縮對話歷史
3. **Agent Teams** — Lead Agent + Teammate Agents + 共享任務列表
4. **1M Context (beta)** — 超過 200K 部分加價（$10/$37.50 per MTok）

## 4.6 Breaking Changes

1. **Prefill 移除** — assistant message 預填內容會回 400 error
2. **Tool 參數引號處理** — 更嚴格，需檢查 tool_use 解析
3. **Extended Thinking 廢棄** — 改用 Adaptive Thinking

## 4.5 如何逼近 4.6 效果

| 場景 | 4.6 原生能力 | 4.5 替代方案 | 能否追平 |
|------|-------------|-------------|---------|
| 複雜推理 | Adaptive Thinking | 手動 CoT + Extended Thinking 開高 budget | ❌ 只能縮小差距 |
| 長 context | 1M + Compaction | 手動分段/摘要後餵入 | ❌ 結構限制 |
| 多 Agent | Agent Teams | 自建 orchestrator | ⚠️ 功能可達但效率差 |
| 標準 coding | 同等 | 直接用 | ✅ 差異極小 |

## 結論

- 日常 coding / SWE 任務：兩者差異可忽略
- 複雜推理 + 長文本 + 多 agent：4.6 有結構性優勢，prompt 技巧只能縮小差距
- 創意寫作：4.5 可能反而更好（部分用戶回報 4.6 寫作品質下降）
- 升級建議：coding/reasoning 場景直接升，寫作場景保留 4.5 備用

---
title: "費用控制規則"
type: concept
tags: [admin, ops, cost, budget]
sources: []
related: [monitoring-metrics, service-management-sop]
created: 2026-07-08
updated: 2026-07-08
status: developing
---

# 費用控制規則

## 每日費用上限

| 資源類別 | 每日上限 (USD) | 說明 |
|---------|--------------|------|
| LLM API（Claude） | $5.00 | 所有 Agent 共用額度 |
| LLM API（備用模型） | $2.00 | fallback 用途 |
| 雲端運算（EC2/Container） | $3.00 | 運行時數計費 |
| 資料庫（MongoDB Atlas） | $1.00 | 儲存 + 讀寫 IOPS |
| 總計 | **$11.00** | 硬上限，不可超過 |

## 預警門檻

| 階段 | 觸發條件 | 動作 |
|------|---------|------|
| 🟡 Level 1 | 達到每日預算 60% | 記錄日誌，發送通知到管理群組 |
| 🟠 Level 2 | 達到每日預算 80% | 降低非核心 Agent 的請求頻率 |
| 🔴 Level 3 | 達到每日預算 95% | 暫停所有非緊急 LLM 請求 |
| 🚨 Hard Stop | 達到每日預算 100% | 強制停止所有 LLM API 呼叫 |

## 超支處理流程

### 自動處理

1. **即時**: 觸發 Level 3 時，系統自動將 Agent 切換為 `economy mode`
2. **降級策略**: 使用較便宜的模型（如 Haiku）處理低優先級任務
3. **佇列暫停**: 非即時任務進入佇列，等待隔日額度恢復
4. **通知**: 自動發送 Telegram 通知給管理員

### 人工介入

1. 管理員收到通知後，評估是否需要臨時追加額度
2. 追加額度需記錄原因，並在 `log.md` 中標註
3. 連續 3 天觸發 Level 2 → 需檢討 Agent 使用模式

## Token 預算分配

| Agent | 每日 Token 額度 | 優先級 |
|-------|---------------|--------|
| admin-agent | 50,000 | HIGH |
| analyst-agent | 100,000 | MEDIUM |
| developer-agent | 80,000 | MEDIUM |
| researcher-agent | 60,000 | LOW |
| 共用池（彈性） | 50,000 | - |

## 費用追蹤方式

```yaml
# 每次 LLM 呼叫記錄
cost_log:
  timestamp: "2026-07-08T10:30:00Z"
  agent: "admin-agent"
  model: "claude-sonnet-4"
  input_tokens: 1200
  output_tokens: 800
  cost_usd: 0.012
  task_type: "monitoring"
```

## 月度檢討

| 檢查項目 | 頻率 | 負責人 |
|---------|------|--------|
| 各 Agent Token 使用分析 | 每週 | admin-agent |
| 費用趨勢報告 | 每月 | admin-agent |
| 預算調整建議 | 每月 | 管理員 |
| 模型選用優化 | 每季 | admin-agent |

## 節費策略

- **Prompt 快取**: 重複的 system prompt 啟用快取，減少 input token
- **摘要壓縮**: 長對話歷史先摘要再送入，降低 context 長度
- **批次處理**: 合併小請求為單次大請求，減少 overhead
- **模型分級**: 簡單任務用 Haiku，複雜分析用 Sonnet/Opus
- **結果快取**: 相同查詢 24h 內使用快取結果

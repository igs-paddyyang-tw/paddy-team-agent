---
title: "監控指標定義"
type: concept
tags: [admin, ops, monitoring, metrics]
sources: []
related: [service-management-sop, cost-control-rules, troubleshooting]
created: 2026-07-08
updated: 2026-07-08
status: developing
---

# 監控指標定義

## 系統資源指標

### CPU 使用率

| 門檻 | 狀態 | 動作 |
|------|------|------|
| < 60% | 🟢 正常 | 無需處理 |
| 60-80% | 🟡 警告 | 記錄日誌，觀察趨勢 |
| > 80% | 🔴 危險 | 發送告警，準備擴容 |
| > 95% 持續 5min | 🚨 緊急 | 自動重啟非核心服務 |

### 記憶體使用量

| 門檻 | 狀態 | 動作 |
|------|------|------|
| < 70% | 🟢 正常 | 無需處理 |
| 70-85% | 🟡 警告 | 檢查是否有 memory leak |
| > 85% | 🔴 危險 | 觸發 GC / 重啟服務 |
| > 95% | 🚨 緊急 | 強制重啟 + 通知管理員 |

- 基準線：Web 服務 < 256MB，Bot 服務 < 128MB，MongoDB < 512MB
- 監控頻率：每 30 秒採樣一次

## API 效能指標

### 回應時間（Response Time）

| 端點類別 | P50 目標 | P95 目標 | P99 上限 |
|---------|---------|---------|---------|
| Health check | < 10ms | < 50ms | < 100ms |
| 資料查詢 API | < 100ms | < 300ms | < 500ms |
| 寫入操作 API | < 200ms | < 500ms | < 1000ms |
| AI 分析請求 | < 3s | < 8s | < 15s |

### 錯誤率

| 指標 | 正常 | 警告 | 危險 |
|------|------|------|------|
| HTTP 5xx 率 | < 0.1% | 0.1-1% | > 1% |
| HTTP 4xx 率 | < 5% | 5-10% | > 10% |
| DB 連線失敗率 | 0% | < 0.5% | > 0.5% |
| Bot 訊息投遞失敗率 | < 1% | 1-5% | > 5% |

## Token 用量指標

### LLM API 使用追蹤

| 指標 | 計算方式 | 告警門檻 |
|------|---------|---------|
| 每日 Token 消耗 | input_tokens + output_tokens | > 日預算 80% |
| 單次請求 Token | 單一 API call 的 token 數 | > 4000 tokens |
| 每小時請求數 | 滾動 1h 內的 API calls | > 100 calls/hr |
| 費用累計 | tokens × 單價 | > 日上限 USD |

### Token 優化建議

- 使用 system prompt 快取，減少重複 token
- 長文本用摘要後再送入 LLM
- 設定 max_tokens 避免無限生成
- 批次請求合併處理

## 監控工具與端點

```bash
# 系統狀態 API
GET /api/system/service-status      # 服務狀態
GET /api/health                     # 健康檢查
GET /api/system/metrics             # 效能指標

# 日誌查詢
GET /api/system/logs/web            # Web 日誌
GET /api/system/logs/bot            # Bot 日誌
```

## 告警通知管道

| 嚴重度 | 通知方式 | 回應時限 |
|--------|---------|---------|
| INFO | 日誌記錄 | 下次巡檢 |
| WARN | Telegram 群組通知 | 4 小時內 |
| ERROR | Telegram + 直接 mention | 1 小時內 |
| CRITICAL | Telegram + 電話通知 | 15 分鐘內 |

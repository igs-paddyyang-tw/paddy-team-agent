---
title: "常見故障排除"
type: troubleshooting
tags: [admin, ops, troubleshooting, debug]
sources: []
related: [service-management-sop, monitoring-metrics, deployment-guide]
created: 2026-07-08
updated: 2026-07-08
status: developing
---

# 常見故障排除

## Bot 斷線

### 症狀
- Telegram Bot 無回應
- `/api/system/service-status` 顯示 bot 為 offline
- 日誌出現 `ConnectionError` 或 `Conflict: terminated by other getUpdates`

### 診斷步驟
1. 檢查 Bot 進程: `ps aux | grep bot`
2. 檢查網路: `curl -s https://api.telegram.org/bot<TOKEN>/getMe`
3. 檢查日誌: `tail -50 logs/bot.log`

### 解決方案
| 原因 | 解法 |
|------|------|
| 多個 Bot 實例衝突 | 停止所有實例，只啟動一個 |
| Token 失效 | 重新生成 Token 並更新 `.env` |
| 網路問題 | 檢查防火牆/DNS，確認可達 Telegram API |
| Webhook 衝突 | 呼叫 `deleteWebhook` 後重啟 polling 模式 |

## Agent 超時

### 症狀
- API 回應 504 Gateway Timeout
- Agent 任務卡住不回傳結果
- LLM 呼叫超過 30 秒無回應

### 診斷步驟
1. 檢查 LLM API 狀態: 確認供應商服務正常
2. 檢查 token 用量: 是否觸發限流
3. 檢查 prompt 長度: 是否超過模型 context window

### 解決方案
| 原因 | 解法 |
|------|------|
| LLM API 限流 | 等待冷卻期，或切換備用模型 |
| Prompt 過長 | 截斷歷史對話，使用摘要替代 |
| 模型過載 | 降級使用較快模型（Haiku） |
| 網路延遲 | 檢查 DNS、使用較近區域端點 |

## DB 鎖定

### 症狀
- 寫入操作持續 timeout
- MongoDB 日誌出現 `lock timeout` 或 `write conflict`
- API 回應慢或回傳 500

### 診斷步驟
1. 檢查當前操作: `db.currentOp({"active": true})`
2. 檢查鎖狀態: `db.serverStatus().locks`
3. 檢查連線數: `db.serverStatus().connections`

### 解決方案
| 原因 | 解法 |
|------|------|
| 長時間查詢佔用鎖 | `db.killOp(opId)` 終止問題操作 |
| 缺少索引導致全表掃描 | 新增適當索引 |
| 連線池耗盡 | 增加 `maxPoolSize` 或檢查連線洩漏 |
| 大量寫入衝突 | 實施 retry with backoff 策略 |

### 預防措施
- 所有查詢欄位建立索引
- 設定查詢 timeout（`maxTimeMS: 5000`）
- 監控慢查詢日誌（> 100ms 的操作）

## 記憶體溢出（OOM）

### 症狀
- 服務被 OS Kill（exit code 137）
- `dmesg` 出現 `Out of memory: Killed process`
- Docker container 自動重啟

### 診斷步驟
1. 檢查記憶體: `docker stats` 或 `free -h`
2. 檢查 OOM 記錄: `dmesg | grep -i "out of memory"`
3. 分析記憶體趨勢: 檢查是否持續增長（leak）

### 解決方案
| 原因 | 解法 |
|------|------|
| Memory leak | 定位洩漏程式碼，修復後重新部署 |
| 資料快取過大 | 設定 LRU 快取上限，定期清理 |
| 大檔案處理 | 改用串流處理，避免一次載入 |
| Container 限制太低 | 調整 `mem_limit` 設定（建議 512MB+） |

### 緊急處理
```bash
# 1. 確認哪個容器佔用最多記憶體
docker stats --no-stream

# 2. 重啟問題容器
docker restart <container_name>

# 3. 如果持續發生，臨時增加 swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

## 快速排除流程圖

```
問題發生 → 檢查 /api/health
  ├─ 200 OK → 檢查特定服務日誌
  ├─ 503 → 檢查依賴服務（DB/Redis）
  └─ 無回應 → 檢查容器狀態 → docker ps
       ├─ 容器在跑 → 檢查 port 綁定
       └─ 容器掛了 → docker logs → 根據錯誤修復後重啟
```

---
title: "服務管理 SOP"
type: concept
tags: [admin, ops, sop, service]
sources: []
related: [deployment-guide, monitoring-metrics, troubleshooting]
created: 2026-07-08
updated: 2026-07-08
status: developing
---

# 服務管理 SOP

## 啟動流程

1. **預檢**: 確認環境變數已載入（`.env` 檔案存在且 BOT_TOKEN 有效）
2. **依賴服務**: 確認 MongoDB / Redis 已啟動且可連線
3. **啟動指令**:
   ```bash
   # 單一服務
   python start.py                    # 主應用（含 Web + Bot）
   # Docker 模式
   ./docker-manager.sh start          # 啟動所有容器
   ```
4. **驗證**: 呼叫 `/api/health` 確認回應 200

## 停止流程

1. **優雅關機**: 送出 SIGTERM，等待當前請求完成（timeout 30s）
2. **停止指令**:
   ```bash
   ./docker-manager.sh stop           # Docker 模式
   python start_all_systems.py stop   # 直接模式
   ```
3. **確認**: 檢查 port 5000 已釋放，無殘留 process

## 重啟流程

1. **Rolling restart**（零停機）: 逐一重啟 worker，確認新 worker healthy 後才停舊的
2. **Full restart**: stop → 等 5s → start，適用於設定變更或版本升級
3. **指令**:
   ```bash
   ./docker-manager.sh restart        # Docker full restart
   ```

## 健康檢查

| 端點 | 方法 | 預期回應 | 頻率 |
|------|------|---------|------|
| `/api/health` | GET | `{"status":"ok"}` 200 | 每 30s |
| `/api/system/service-status` | GET | 各服務狀態 JSON | 每 60s |
| MongoDB ping | internal | latency < 100ms | 每 30s |

## 日誌查看

```bash
# Docker 模式
./docker-manager.sh logs             # 即時日誌
docker logs --tail 200 smart-bot-web # 最近 200 行

# 本地模式
tail -f logs/web.log                 # Web 服務日誌
tail -f logs/bot.log                 # Bot 服務日誌
```

## 日誌分級

| Level | 用途 | 保留天數 |
|-------|------|---------|
| ERROR | 需立即處理的異常 | 30 天 |
| WARN  | 潛在問題，需關注 | 14 天 |
| INFO  | 正常操作紀錄 | 7 天 |
| DEBUG | 除錯用，僅開發環境 | 1 天 |

## 注意事項

- 啟動前務必確認無 port 衝突（5000, 27017, 6379）
- 生產環境禁止使用 `kill -9`，應用 graceful shutdown
- 日誌清理使用 `/api/system/clear-logs`，不要手動刪除檔案

---
title: "部署流程指南"
type: concept
tags: [admin, ops, deploy, docker]
sources: []
related: [service-management-sop, monitoring-metrics]
created: 2026-07-08
updated: 2026-07-08
status: developing
---

# 部署流程指南

## Docker 部署

### 前置需求

- Docker Engine ≥ 24.0
- Docker Compose ≥ 2.20
- 可用記憶體 ≥ 2GB
- 磁碟空間 ≥ 10GB（含映像檔）

### 首次部署

```bash
# 1. 準備環境設定
cp .env.example .env
# 編輯 .env 設定 BOT_TOKEN、MONGODB_URI 等

# 2. 建置映像檔
docker compose build --no-cache

# 3. 啟動所有服務
./docker-manager.sh start

# 4. 確認服務健康
curl http://localhost:5000/api/health
```

### 服務架構

| 服務 | Port | 用途 |
|------|------|------|
| nginx | 80/443 | 反向代理、SSL 終止 |
| smart-bot-web | 5000 | 主應用（Flask） |
| mongodb | 27017 | 資料庫 |
| redis | 6379 | 快取、Session |
| analyzer | - | 智能分析器 |

## 環境變數

| 變數名 | 必填 | 說明 | 範例 |
|--------|------|------|------|
| `BOT_TOKEN` | ✅ | Telegram Bot Token | `123456:ABC-DEF` |
| `MONGODB_URI` | ✅ | MongoDB 連線字串 | `mongodb://localhost:27017` |
| `REDIS_URL` | ❌ | Redis 連線（可選） | `redis://localhost:6379` |
| `FLASK_ENV` | ❌ | 執行環境 | `production` |
| `LOG_LEVEL` | ❌ | 日誌層級 | `INFO` |
| `API_RATE_LIMIT` | ❌ | API 限流（req/min） | `60` |

> ⚠️ 生產環境務必設定 `FLASK_ENV=production`，禁用 debug mode

## Rolling Restart（零停機部署）

```bash
# 1. 拉取新版映像
docker compose pull

# 2. 逐一更新服務（Web 先、Bot 後）
docker compose up -d --no-deps --build smart-bot-web
# 等待 health check 通過
sleep 10 && curl -f http://localhost:5000/api/health

# 3. 更新其他服務
docker compose up -d --no-deps --build telegram-bot
docker compose up -d --no-deps --build analyzer
```

## 版本回滾

```bash
# 回滾到前一版本
docker compose down
git checkout v1.3.4.1
docker compose up -d --build

# 或使用映像標籤
docker compose up -d smart-bot-web:v1.3.4.1
```

## 部署檢查清單

- [ ] `.env` 環境變數完整且正確
- [ ] MongoDB 資料庫可連線
- [ ] Port 無衝突（80, 443, 5000, 27017, 6379）
- [ ] SSL 憑證有效（生產環境）
- [ ] 健康檢查端點回應正常
- [ ] 日誌輸出正常，無 ERROR
- [ ] 備份最新資料庫快照

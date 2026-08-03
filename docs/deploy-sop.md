# 部署 SOP — paddy-team-agent

> 最後更新：2026-08-02

## 環境需求

| 項目 | 版本 |
|------|------|
| Python | 3.12+ |
| OS | Linux（推薦 Ubuntu 22.04+） |
| Docker（選用） | 24.0+ |
| ark-team-agent | 最新（pip install） |

## 方式一：直接啟動（開發/單機）

### 1. 環境準備

```bash
cd ~/kiro-cli/projects/paddy-team-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
cp .env.example .env
# 必填：TELEGRAM_BOT_TOKEN
# 選填：POSTGRES_PASSWORD, PLATFORM_API_KEYS
```

### 3. 啟動服務

```bash
# 前景執行
python start.py

# 背景執行（含自動重啟）
nohup bash start-team.sh > logs/team.log 2>&1 &
```

### 4. 驗證

```bash
curl http://localhost:33333/health
# 預期：{"status": "ok"}
```

## 方式二：Docker Compose（生產）

### 1. 啟動

```bash
cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN 和 POSTGRES_PASSWORD

docker compose -f docker-compose.prod.yml up -d --build
```

### 2. 驗證

```bash
docker compose -f docker-compose.prod.yml ps
curl http://localhost:33333/health
```

### 3. 查看日誌

```bash
docker compose -f docker-compose.prod.yml logs -f telegram-bot
docker compose -f docker-compose.prod.yml logs -f backend
```

## 重啟流程

### 正常重啟（不中斷服務）

```bash
# 方法 A：restart.flag（start-team.sh 模式）
touch restart.flag
kill $(cat team.pid)
# start-team.sh 會自動偵測 flag 並重啟

# 方法 B：Docker
docker compose -f docker-compose.prod.yml restart telegram-bot
```

### 緊急重啟（強制）

```bash
# 直接啟動
kill -9 $(cat team.pid) 2>/dev/null
python start.py

# Docker
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

## 健康檢查

| 端點 | 用途 |
|------|------|
| `GET /health` | 服務存活 |
| `GET /status` | 所有 agent 狀態 |
| heartbeat 檔案 | `state/heartbeat`（Unix timestamp） |

### 判斷服務異常

```bash
# heartbeat 超過 5 分鐘未更新 = 異常
LAST=$(cat state/heartbeat)
NOW=$(date +%s)
DIFF=$((NOW - LAST))
if [ $DIFF -gt 300 ]; then echo "⚠️ 服務異常"; fi
```

## 常見問題

| 症狀 | 原因 | 解法 |
|------|------|------|
| Bad Gateway | Telegram API 限流/網路不穩 | 等待 1-2 分鐘自動恢復，或重啟 |
| agent process died 循環 | Worker 啟動過快觸發 rate limit | 重啟主進程，間隔拉長 |
| ModuleNotFoundError | venv 未啟用或套件未裝 | `source .venv/bin/activate && pip install -r requirements.txt` |
| port 33333 already in use | 殘留進程 | `kill $(lsof -t -i:33333)` |

## 備份

```bash
# 狀態資料備份
cp -r state/ backups/state-$(date +%Y%m%d)/

# 重要檔案
# - .env（密鑰）
# - team.yaml（團隊配置）
# - state/*.db（運行狀態）
# - knowledge/（知識庫）
```

## 成本控制

`team.yaml` 中已設定：
- `daily_limit_usd: 30.0` — 每日上限
- `warn_at_percentage: 80` — 80% 預警

超過限額服務會自動暫停，需手動確認後恢復。

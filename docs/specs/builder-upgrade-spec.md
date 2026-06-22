# ark-agent-team-builder → ai-team-agent 完整差異分析

> 目標：`build_team.py` 預設產出與 `ai-team-agent` 一模一樣的完整平台

---

## 差異對照表

| 模組 | Builder 目前產出 | ai-team-agent 實際 | 差異 |
|------|-----------------|-------------------|------|
| **start.py** | 舊版 daemon（78 行） | 統一入口 5 服務（279 行） | ★ 重寫 |
| **src/ark_team_core/** | 5 模組（282 行） | 同（含 EventBus emit） | process.py 需升級 |
| **src/backend/api/** | ❌ 不存在 | 6 檔（router/agents/issues/admin/ws/auth） | ★ 新增 |
| **src/backend/db/** | ❌ 不存在 | models.py + 001_init.sql（7 表） | ★ 新增 |
| **src/backend/events/** | ❌ 不存在 | types.py + bus.py（14 事件） | ★ 新增 |
| **src/backend/services/** | ❌ 不存在 | cost_tracker + audit_logger + health_monitor | ★ 新增 |
| **src/tg_ui/** | ❌ 不存在 | 8 檔（bot/formatters/notifications/progress/topics/handlers×3） | ★ 新增 |
| **src/{project}/telegram_adapter.py** | ✅ 產出（舊版） | ❌ 已刪除 | ★ 移除 |
| **Dockerfile** | ❌ 不存在 | 23 行 | ★ 新增 |
| **docker-compose.prod.yml** | ❌ 不存在 | 74 行 | ★ 新增 |
| **tests/** | ❌ 不存在 | test_api.py（109 行） | ★ 新增 |
| **apps/web/** | ❌ 不存在 | Next.js 8 頁面（944 行 TS） | ★ 新增（選配） |
| **requirements.txt** | 基本（6 套件） | 完整（+fastapi+uvicorn） | ★ 更新 |

---

## 數字摘要

| 項目 | Builder 目前 | ai-team-agent 實際 | 需新增 |
|------|-------------|-------------------|--------|
| Python 檔案 | 12 | 39 | +27 |
| Python 行數 | ~800 | 2,426 | +1,626 |
| Web 檔案 | 0 | 22 | +22（選配） |
| Web 行數 | 0 | 944 | +944（選配） |
| 根目錄檔案 | 10 | 13 | +3 |

---

## 修改方案

### build_team.py 需新增的函式

```python
# 現有（保留）
_write_team_yaml()
_write_scheduler_yaml()
_write_start_py()           # ★ 替換為新版統一入口
_write_minimal_core()       # ★ 已升級（5 模組）
_scaffold_agents()
_write_start_team_sh()
_write_readme()

# 新增
_write_backend_api(dst)     # 6 檔：router/agents/issues/admin/ws/auth
_write_backend_db(dst)      # models.py + 001_init.sql
_write_backend_events(dst)  # types.py + bus.py
_write_backend_services(dst)# cost_tracker + audit_logger + health_monitor
_write_tg_ui(dst)           # 8 檔：bot/formatters/notifications/progress/topics/handlers×3
_write_dockerfile(dst)      # Dockerfile
_write_docker_compose(dst)  # docker-compose.prod.yml
_write_tests(dst)           # test_api.py

# 移除
_write_telegram_adapter()   # 不再產出舊版
```

### start.py 模板差異

```diff
- from {project}.telegram_adapter import TelegramAdapter
- adapter = TelegramAdapter(daemon)
- await adapter.start()

+ from backend.api.router import app
+ import uvicorn
+ from backend.events.bus import EventBus
+ from tg_ui.handlers.commands import cmd_start, cmd_status, ...
+ from tg_ui.notifications import NotificationService
+
+ # 1. DB + EventBus
+ # 2. uvicorn(app)
+ # 3. Agent Daemon (spawn mode)
+ # 4. TG Bot (11 指令)
+ # 5. Scheduler
```

### requirements.txt 差異

```diff
  pyyaml>=6.0
  python-telegram-bot[ext]>=21.0
  python-dotenv>=1.0.0
  httpx>=0.25.0
  apscheduler>=3.10.0
+ fastapi>=0.110.0
+ uvicorn>=0.27.0
+ swr  # web only
```

---

## 實作步驟

| # | 步驟 | 預估行數 |
|---|------|---------|
| 1 | 替換 `_write_start_py()` 為新版統一入口模板 | +200 |
| 2 | 新增 `_write_backend_api()` — 嵌入 6 個 API 檔案 | +520 |
| 3 | 新增 `_write_backend_db()` — models + migration | +140 |
| 4 | 新增 `_write_backend_events()` — types + bus | +100 |
| 5 | 新增 `_write_backend_services()` — 3 個 service | +205 |
| 6 | 新增 `_write_tg_ui()` — 8 個 TG 模組 | +710 |
| 7 | 新增 `_write_dockerfile()` + `_write_docker_compose()` | +100 |
| 8 | 新增 `_write_tests()` | +110 |
| 9 | 移除 `telegram_adapter.py` 產出 | -80 |
| 10 | 更新 requirements.txt 模板 | +3 |
| **合計 build_team.py 增加** | | **~2,000 行** |

---

## 驗證方式

```bash
# 產出新專案
python build_team.py /tmp/test-full

# 驗證結構
diff <(find /tmp/test-full/src -name "*.py" | sort) \
     <(find ai-team-agent/src -name "*.py" | sort | sed 's|ai-team-agent/||')

# 驗證可啟動
cd /tmp/test-full && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import sys; sys.path.insert(0,'src'); from backend.api.router import app; print('OK')"

# 跑測試
python tests/test_api.py
```

---

## 注意事項

1. **不產出 apps/web/**（Web Dashboard 為選配，需 Node.js 20+，用 `--with-web` flag）
2. **src/{project}/** 目錄保留（event_log + api + mcp_setup），但移除 `telegram_adapter.py`
3. **process.py** 已在 `_write_minimal_core()` 中，需確認是 spawn 模式（非 stdin）
4. **命名空間**：TG 模組用 `tg_ui/`（避免與 `python-telegram-bot` 的 `telegram` 衝突）
5. **build_team.py 會超過 3,000 行**——考慮拆分為多個 `_generators/` 模組

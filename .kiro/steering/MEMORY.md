# Memory

## 專案狀態（2026-08-03）

- **版本**：v1.1.0（定版）
- **架構**：依賴 ark_team_agent 套件（pip install），不再有自有 src/
- **服務**：5 agents 全部正常啟動，scheduler 6 jobs 載入完成
- **Port**：33333

## 定版結構

```
paddy-team-agent/
├── start.py              # 入口（5 行）
├── team.yaml             # 團隊配置（5 agents）
├── scheduler.yaml        # 排程（6 jobs）
├── .env                  # TELEGRAM_BOT_TOKEN（不進版控）
├── agents/               # 5 個 agent 工作目錄
│   ├── admin-agent/
│   ├── leader-agent/
│   ├── ai-dev-agent/
│   ├── coder-agent/
│   └── qa-agent/
├── knowledge/            # 共享知識庫
│   ├── hoyeah/
│   └── shared/
├── docs/                 # 架構文件
├── scripts/              # 維運腳本
├── workflows/            # Workflow YAML
│   └── daily-news-team.yaml
└── pyproject.toml
```

## 技術決策

- LLM 後端：kiro-cli（spawn per message）
- 套件：ark_team_agent（GitHub Release whl，pip install）
- DB：SQLite（state/ 目錄）
- Port：33333（health_port in team.yaml）
- Scheduler：APScheduler，設定在 scheduler.yaml 根目錄

## 踩坑紀錄（2026-08-03）

- `scheduler.yaml` 欄位：`id` → `name`（套件 ScheduledJobConfig 只有 name）
- agent json 路徑：`file://.kiro/` → `file://../../.kiro/`（從 `.kiro/agents/` 往上兩層才到 agent 根目錄）
- leader-agent json 檔名是 `pm-agent.json`（舊命名遺留，不影響運作）

## 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| v1.1.0 | 2026-08-03 | 定版清理（-132174 行），scheduler/agent 路徑修正 |
| v1.1.0-rc | 2026-07-31 | 改用 ark-team-agent 套件，移除自有 src/ |
| v1.0.0 | 2026-07-29 | 補齊 wiki/memory/skill/runtime 子系統 |

# paddy-team-agent `v1.1.0`

> Paddy 個人 AI Agent 團隊 — 基於 [ark-team-agent](https://github.com/igs-paddyyang-tw/ark_team_agent) 套件

[![Version](https://img.shields.io/badge/version-1.1.0-orange)](https://github.com/igs-paddyyang-tw/paddy-team-agent)
[![ark-team-agent](https://img.shields.io/badge/ark--team--agent-1.0.1-blue)](https://github.com/igs-paddyyang-tw/ark_team_agent/releases/tag/v1.0.1)

---

## 快速開始

```bash
git clone https://github.com/igs-paddyyang-tw/paddy-team-agent.git
cd paddy-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install https://github.com/igs-paddyyang-tw/ark_team_agent/releases/download/v1.0.1/ark_team_agent-1.0.1-py3-none-any.whl
cp .env.example .env   # 填入 TELEGRAM_BOT_TOKEN
python start.py
```

**需求**：Python ≥ 3.11、[Kiro CLI](https://kiro.dev) 已安裝

---

## 架構

```
ark-team-agent（套件）
        │  pip install
        ▼
paddy-team-agent（部署）
├── team.yaml        # 團隊配置
├── scheduler.yaml   # 排程設定
├── agents/          # 5 個 agent 工作目錄
├── knowledge/       # 共享知識庫
├── workflows/       # Workflow YAML
└── start.py         # 5 行入口
```

---

## 團隊

| Agent | Role | 職責 |
|-------|------|------|
| admin-agent | 👑 admin | 服務管理、開發維護、團隊指揮 |
| leader-agent | 🧠 leader | 需求分析、任務拆解、派工、驗收 |
| ai-dev-agent | 🤖 worker | AI/ML 架構、Prompt 工程、Agent 設計 |
| coder-agent | 💻 worker | 全端開發、API 實作、程式碼產出 |
| qa-agent | 🧪 worker | 測試、品質保證、Code Review |

---

## 排程（scheduler.yaml）

| Job | Cron | 說明 |
|-----|------|------|
| hourly-check | 每小時 09-21 點 | 團隊狀態回報（admin） |
| daily-summary | 21:00 | 今日摘要（leader） |
| daily-ops-report | 21:05 | 系統管理摘要（admin） |
| daily-knowledge-digest | 21:30 | 廣播知識沉澱（admin） |
| wiki-ingest | 22:00 | 知識庫自動 ingest（admin） |
| daily-news | 08:30 週一~五 | 科技日報（ai-dev） |

---

## 目錄結構

```
paddy-team-agent/
├── start.py              # 入口（5 行）
├── team.yaml             # 團隊配置
├── scheduler.yaml        # 排程
├── .env                  # 環境變數（不進版控）
├── agents/               # Agent 工作目錄
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
└── pyproject.toml        # v1.1.0
```

---

## 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| **v1.1.0** | 2026-08-03 | 定版清理，scheduler/agent 路徑修正，5/5 agents 驗證通過 |
| v1.1.0-rc | 2026-07-31 | 改用 ark-team-agent 套件，移除自有 src/（-4876 行） |
| v1.0.0 | 2026-07-29 | 補齊 wiki/memory/skill/runtime 子系統 |

舊版 src/ 備份：`backup/src-legacy-v1.0.0` branch

---

## 相關 Repos

| Repo | 說明 |
|------|------|
| [ark_team_agent](https://github.com/igs-paddyyang-tw/ark_team_agent) | 框架套件（來源：nana-team-agent） |
| [nana-team-agent](https://github.com/igs-paddyyang-tw/nana-team-agent) | 框架開發源 |

---

## 授權

MIT

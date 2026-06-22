# Workshop × Skill 對照表

> 原則：一鍵安裝（build script 全自動產出），教學專注於架構理解和使用方式。

---

## 總覽

| Workshop | 時長 | 一鍵指令 | 學什麼 |
|----------|------|---------|--------|
| 01 AI Bot | 40 min | `python build_bot.py my-bot` | 單一 Bot 對話架構 |
| 02 Agent Team | 50 min | `python build_team.py my-team` | 多 Agent 協作架構 |
| 03 Platform | 90 min | （同上，教進階功能） | API + Web + A2A 全棧 |
| 04 Skills | 60 min | `ark-skill-creator` AI 自動產出 | Skill 架構 + AI 協作產出 + 評估迴圈 |

---

## Workshop 01：AI Bot

### 一鍵安裝

```bash
python .kiro/skills/ark-ai-bot-builder/scripts/build_bot.py my-bot
cd my-bot && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 填 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start_bot.py
```

### 使用到的 Skills

| Skill | 用途 | 觸發方式 |
|-------|------|---------|
| `ark-ai-bot-builder` | 一鍵產出完整 Bot workspace | `build_bot.py` |
| `ark-env-doctor` | 環境檢查 | 聊天框輸入「檢查環境」 |

### 教學重點（架構理解）

```
使用者 → Telegram → ConversationPlanner（意圖路由）
                         │
                         ├── 閒聊 → Gemini Chat（秒回）
                         ├── 新聞 → news_scraper → renderer
                         └── 程式 → Agent CLI（codegen）
```

學員理解：
- Bot 不是「一個 LLM」，是「路由 + 多 Skill」
- Planner 決定走哪條路
- Gemini 做簡單對話，Agent CLI 做複雜任務

---

## Workshop 02：Agent Team

### 一鍵安裝

```bash
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team
cd my-team && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 填 TELEGRAM_BOT_TOKEN
python start.py
```

### 使用到的 Skills

| Skill | 用途 | 觸發方式 |
|-------|------|---------|
| `ark-agent-team-builder` | 產出完整平台（93 項） | `build_team.py` |
| `ark-kiro-init` | 批次產出 .kiro/ 配置 | `build_kiro.py` |
| `ark-env-doctor` | 環境檢查 | 聊天框輸入「檢查環境」 |

### 教學重點（架構理解）

```
使用者 → TG Bot → 智慧路由
                     │
                     ├── 簡單問題 → Gemini 秒回
                     └── 複雜任務 → A2A Router
                                      │
                                      ├── Discovery（匹配 Agent）
                                      ├── TaskGraph（依賴排序）
                                      └── spawn kiro-cli
                                            │
                              ┌──────────────┼──────────────┐
                              pm-agent    coder-agent    qa-agent
```

學員理解：
- 5 個 Agent 各有角色和 Skills
- Leader 拆解 → Worker 執行 → 自動串接
- A2A Discovery 自動匹配「誰做什麼」
- 不用手動寫一行程式碼

---

## Workshop 03：Platform（進階）

### 安裝（使用 Workshop 02 同一個專案）

```bash
# 無需重新安裝 — 在 Workshop 02 的 my-team 上繼續
cd my-team

# 啟動 Web Dashboard
cd apps/web && npm install && npm run dev

# 測試 API
curl http://localhost:33333/api/admin/dashboard/stats
```

### 使用到的 Skills

| Skill | 用途 | 觸發方式 |
|-------|------|---------|
| `ark-superpowers` | 產出規格/設計/計畫文件 | 聊天框輸入「寫 spec」 |
| `ark-code-spec-validator` | 驗證 code 與 spec 一致性 | 「分析 spec 差異」 |
| `ark-frontend-design` | Web UI 設計 | 「設計 Dashboard」 |
| `ark-docker-deploy` | Docker 部署 | 「Docker 部署」 |

### 教學重點（架構理解）

```
四層架構：
入口層（TG + Web）→ 協調層（API + EventBus + A2A）→ 執行層（Agents）→ 知識層（Skills + KB）
```

學員理解：
- Backend API 21 端點（CRUD + Admin + WebSocket）
- EventBus 事件驅動（14 事件 → 費用/審計/通知）
- A2A 協作（TaskGraph + FeedbackLoop）
- Web Dashboard 即時監控
- Docker 一鍵部署

---

## Workshop 04：Skill 開發

### 一鍵安裝

```bash
# 在 Kiro 聊天框輸入：
建立新 Skill：每日科技新聞日報，抓取指定 RSS 來源，產出精美 HTML 日報頁面，可直接用瀏覽器開啟分享網址
```

`ark-skill-creator` 自動產出：
- `SKILL.md`（觸發條件 + 執行指引）
- `scripts/`（news_scraper + html_renderer）
- `templates/`（HTML 日報模板）
- `evals/evals.json`（測試案例）
- 跑評估 → 優化 → 重跑 → 直到滿意

產出後使用：
```bash
# TG 對 Bot 說：
今天有什麼科技新聞

# Bot 自動：抓新聞 → 產出 HTML → 回傳檔案/網址
# 瀏覽器開啟 output/tech-daily.html
```

### 使用到的 Skills

| Skill | 用途 | 觸發方式 |
|-------|------|---------|
| `ark-skill-creator` | AI 產出 + 評估 + 迭代 Skill | 「建立新 Skill」 |
| `ark-superpowers` | 寫 Skill 的規格文件 | 「寫 spec」 |
| `ark-code-review` | 檢查 Skill 品質 | 「review 程式碼」 |

### 教學重點

```
自然語言描述需求
    │
    ▼
ark-skill-creator AI 產出
    │
    ├── SKILL.md（description + 指令）
    ├── scripts/（可執行碼）
    └── evals/（測試案例）
    │
    ▼
自動評估（跑測試 + 評分）
    │
    ├── 觸發率低 → AI 優化 description
    ├── 輸出品質差 → AI 改寫指令
    └── 通過 → 發佈
```

學員理解：
- **不是手寫 SKILL.md** — 用 AI 產出，人類只負責「描述需求」和「確認品質」
- Skill 架構三層揭露：metadata → SKILL.md → references/
- description 決定觸發時機（AI 優化觸發精度）
- 評估迴圈：產出 → 測試 → 回饋 → 重寫 → 測試
- 好的 Skill = 好的 description + 好的指令 + 好的範例

---

## 完整 Skill 使用清單

| Skill | W01 | W02 | W03 | W04 | 說明 |
|-------|:---:|:---:|:---:|:---:|------|
| `ark-ai-bot-builder` | ★ | | | | 一鍵產出 Bot |
| `ark-agent-team-builder` | | ★ | | | 一鍵產出 Team |
| `ark-kiro-init` | | ★ | | | 配置 .kiro/ |
| `ark-env-doctor` | ✓ | ✓ | | | 環境檢查 |
| `ark-superpowers` | | | ★ | ✓ | 規格/設計/計畫文件 |
| `ark-code-spec-validator` | | | ★ | | Spec vs Code 驗證 |
| `ark-frontend-design` | | | ✓ | | Web UI |
| `ark-docker-deploy` | | | ✓ | | Docker |
| `ark-skill-creator` | | | | ★ | Skill 開發 |
| `ark-code-review` | | | | ✓ | 品質檢查 |

★ = 核心（必用）　✓ = 輔助（選用）

---

## 安裝前置條件

| 項目 | W01 | W02 | W03 | W04 |
|------|:---:|:---:|:---:|:---:|
| Python 3.12+ | ✅ | ✅ | ✅ | ✅ |
| Kiro CLI | | ✅ | ✅ | ✅ |
| Git | ✅ | ✅ | ✅ | ✅ |
| Node.js 20+ | | | ✅ | |
| Telegram Token | ✅ | ✅ | | |
| Gemini API Key | ✅ | ✓ | | |
| Docker | | | ✓ | |

---

## 教學節奏

```
每個 Workshop 的標準流程：
1. 一鍵安裝（5 min）— build script 自動產出
2. 架構說明（10 min）— 看圖理解資料流
3. 啟動 + 體驗（10 min）— 跑起來、發訊息看結果
4. 深入解說（15-50 min）— 各元件職責、如何修改
5. 動手練習（10-20 min）— 改設定、加 Agent、改 Skill
```

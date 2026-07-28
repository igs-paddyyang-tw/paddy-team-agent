---
title: "Agent 系統提詞 + Skills + 知識庫 全面對齊計畫"
type: onepager
status: draft
language: zh-TW
created: 2026-06-25
author: admin-agent
tags: [alignment, soul, skills, knowledge, agents, ark-kiro-init]
---

# Agent 系統提詞 + Skills + 知識庫 全面對齊計畫

## 問題

ark-kiro-init v2.0 模板已升級（人格+自我成長+多層知識庫），但實際 agents 沒有同步。

### 差距矩陣

| 維度 | 模板（ark-kiro-init v2.0） | 實際 agents | 差距 |
|------|--------------------------|-------------|------|
| 人格段 `🎭` | ❌ 模板缺（只在 persona-presets） | ✅ 有 | 模板要補 |
| 自我成長段 `📚` | ✅ 有 | ❌ 沒有 | 實際要補 |
| 知識庫層級 `📂` | ✅ 有 | ❌ 沒有 | 實際要補 |
| schema.md 版本 | v3.1（三層+自我成長） | v3.0（基礎） | 實際要升級 |
| `knowledge/shared/` | 模板定義 | 不存在 | 要新建 |
| `ark-grill-me` | workshop 04 核心 | 無 Agent 安裝 | 要補裝 |
| `ark-news-daily` | workshop 教學用 | 無 Agent 安裝 | 要補裝 |
| `ark-web-scraper` | workshop 01 核心 | 無 Agent 安裝 | 要補裝 |

---

## 執行計畫（4 步驟）

### Step 1：SOUL.md 全面對齊（模板 ← 實際 → 模板）

#### 1a. 模板補入人格段

在 `ark-kiro-init/assets/steering/SOUL-*.md` 加入 `🎭 人格與語氣` 段，引用 `references/persona-presets.md` 依角色填充。

#### 1b. 實際 agents 補入自我成長段

在 5 個 Agent 的 SOUL.md 追加：

```markdown
## 📚 自我成長

- 每完成一個任務，反思「學到什麼」→ 寫入 knowledge/wiki/
- 使用 [[wikilink]] 連結相關知識頁面
- 查詢前先搜尋自己的 knowledge/，優先使用已有知識
- 找不到才搜尋根目錄 knowledge/shared/（共用知識）
- 不確定的知識標記 (?)，不要編造
- 每日結束更新 knowledge/wiki/overview.md 反映能力成長

## 📂 知識庫層級

| 優先 | 位置 | 說明 |
|------|------|------|
| 1️⃣ | 自己的 knowledge/ | 預設讀寫位置 |
| 2️⃣ | 根目錄 knowledge/shared/ | 共用知識（排程彙整） |
| 3️⃣ | 根目錄 knowledge/ | 團隊知識（IDE 手動維護） |
```

---

### Step 2：knowledge/schema.md 升級 v3.0 → v3.1

用 `references/knowledge-schema-template.md` 內容覆蓋 5 個 Agent 的 schema.md。

新增內容：
- 三層架構圖
- 讀取優先順序表
- 寫入規則表
- 共用知識同步機制圖
- 自我成長觸發時機表
- 禁止事項

---

### Step 3：補裝缺少的 Skills

| Skill | 補裝到 | 理由 |
|-------|--------|------|
| `ark-grill-me` | leader-agent, ai-dev-agent | Workshop 04 核心（設計拷問），leader/dev 必備 |
| `ark-news-daily` | admin-agent | Workshop 教學用 + 排程日報能力 |
| `ark-web-scraper` | coder-agent, ai-dev-agent | Workshop 01 核心（資料抓取） |

---

### Step 4：根目錄建立 knowledge/shared/

```bash
mkdir -p knowledge/shared/{raw,wiki}
# shared/schema.md — 共用知識庫規則
# shared/index.md — 共用索引
# shared/log.md — 操作日誌
```

---

## 完成後的完整 SOUL.md 結構

```markdown
# 👑 {Role} — {Description}

## 🧠 Your Identity（身份）
## 🎯 Your Core Mission（職責）
## 🚨 Critical Rules（規則）
## 💭 Communication Style（溝通風格）
## 🎭 人格與語氣（NEW — persona-presets）
## 📚 自我成長（NEW — 知識累積指令）
## 📂 知識庫層級（NEW — 三層讀取優先）
## ⚙️ Tool Settings
```

---

## 修改清單

| # | 檔案 | 動作 |
|---|------|------|
| 1 | `ark-kiro-init/assets/steering/SOUL-admin.md` | 補入 🎭 人格段 |
| 2 | `ark-kiro-init/assets/steering/SOUL-leader.md` | 補入 🎭 人格段 |
| 3 | `ark-kiro-init/assets/steering/SOUL-worker.md` | 補入 🎭 人格段 |
| 4 | `agents/admin-agent/.kiro/steering/SOUL.md` | 補入 📚 + 📂 |
| 5 | `agents/leader-agent/.kiro/steering/SOUL.md` | 補入 📚 + 📂 |
| 6 | `agents/ai-dev-agent/.kiro/steering/SOUL.md` | 補入 📚 + 📂 |
| 7 | `agents/coder-agent/.kiro/steering/SOUL.md` | 補入 📚 + 📂 |
| 8 | `agents/qa-agent/.kiro/steering/SOUL.md` | 補入 📚 + 📂 |
| 9 | `agents/*/knowledge/schema.md` × 5 | 升級 v3.0 → v3.1 |
| 10 | `knowledge/shared/` | 新建目錄 + schema + index + log |
| 11 | `agents/leader-agent/.kiro/skills/ark-grill-me/` | 補裝 |
| 12 | `agents/ai-dev-agent/.kiro/skills/ark-grill-me/` | 補裝 |
| 13 | `agents/ai-dev-agent/.kiro/skills/ark-web-scraper/` | 補裝 |
| 14 | `agents/coder-agent/.kiro/skills/ark-web-scraper/` | 補裝 |
| 15 | `agents/admin-agent/.kiro/skills/ark-news-daily/` | 補裝 |
| 16 | `ark-kiro-init/SKILL.md` | 版本 2.0 → 2.1 |
| 17 | `ark-kiro-init/references/role-skills-map.md` | 更新對照表 |

---

## 驗收條件

- [ ] 5 個 Agent SOUL.md 都有 🎭 + 📚 + 📂 三段
- [ ] 5 個 Agent schema.md 都是 v3.1（含三層架構 + 自我成長規則）
- [ ] `knowledge/shared/` 存在且有 schema + index + log
- [ ] `ark-grill-me` 安裝在 leader-agent + ai-dev-agent
- [ ] `ark-web-scraper` 安裝在 coder-agent + ai-dev-agent
- [ ] `ark-news-daily` 安裝在 admin-agent
- [ ] `ark-kiro-init` 模板 SOUL-*.md 都有 🎭 + 📚 + 📂
- [ ] `ark-kiro-init` version = 2.1

## 預估工時

45 分鐘。

---

*使用 ark-superpowers 框架產出。*

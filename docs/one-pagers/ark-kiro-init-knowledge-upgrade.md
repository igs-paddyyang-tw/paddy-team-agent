---
title: "ark-kiro-init 升級：Agent 自我成長知識庫 + 角色 Skills 預裝"
type: onepager
status: draft
language: zh-TW
created: 2026-06-25
author: admin-agent
tags: [ark-kiro-init, knowledge, skills, self-evolution, L5]
---

# ark-kiro-init 升級：Agent 自我成長知識庫 + 角色 Skills 預裝

## 問題

1. `build_kiro.py` 產出的 `.kiro/skills/` 是空目錄 → Agent 沒有任何可用能力
2. `knowledge/` 五件套是空白 → Agent 不知道如何自我成長
3. SOUL.md 沒有指示 Agent 使用/更新知識庫 → 知識不會累積

## 目標

- Agent 啟動後即有角色對應的 Skills（不需手動 clone）
- Agent 完成任務後自動將經驗寫入 knowledge/wiki/
- Agent 查詢問題前優先搜尋自己的知識庫

## 非目標

- 不改 runtime 程式碼
- 不改 A2A 協議
- 不新增 MCP Tool

## 方案

### 1. 角色 → Skills 對照表

| 角色 | 預裝 Skills |
|------|------------|
| 全員 | `ark-wiki-engine` |
| admin | +（無額外） |
| leader | + `ark-superpowers` + `ark-code-spec-validator` + `ark-project-planning` + `ark-uml-generator` + `ark-doc-coauthoring` |
| ai-dev | + `ark-skill-creator` + `ark-grill-me` + `ark-superpowers` |
| coder | + `ark-skill-creator` + `ark-code-review` |
| qa | + `ark-code-spec-validator` + `ark-code-review` |
| devops | + `ark-docker-deploy` |

### 2. knowledge/schema.md 自我成長規則

```markdown
## 自我成長規則

| 觸發時機 | 動作 | 寫入位置 |
|---------|------|---------|
| 完成任務後 | 萃取學到的技巧/模式 | wiki/{category}/ |
| 遇到問題並解決 | 記錄問題 + 解法 | wiki/troubleshooting/ |
| 收到 Spec/Design | 存入 raw/ | raw/ |
| 每日結束 | 更新 overview.md | wiki/overview.md |
```

### 3. SOUL.md 加入自我成長段

```markdown
## 📚 自我成長

- 每完成一個任務，反思「學到什麼」→ 寫入 knowledge/wiki/
- 使用 [[wikilink]] 連結相關知識頁面
- 查詢前先搜尋 knowledge/，優先使用已有知識
- 不確定的知識標記 (?)，不要編造
```

### 4. knowledge/wiki/overview.md 預置角色能力

```markdown
---
title: "{role} 能力概覽"
type: overview
tags: [overview, {role}]
created: {date}
updated: {date}
status: seedling
---

# {role} 能力概覽

## 已安裝 Skills
- ark-wiki-engine（知識管理）
- ...（依角色）

## 知識領域
- （待填充，隨任務累積自動成長）

## 學習記錄
- （Agent 完成任務後自動追加）
```

## 修改清單

| # | 檔案 | 動作 |
|---|------|------|
| 1 | `scripts/build_kiro.py` | 加入 `_install_role_skills()` 函式 |
| 2 | `assets/steering/SOUL-admin.md` | 加入自我成長段 |
| 3 | `assets/steering/SOUL-leader.md` | 加入自我成長段 |
| 4 | `assets/steering/SOUL-worker.md` | 加入自我成長段 |
| 5 | `references/role-skills-map.md` | 新增（角色 Skills 對照表） |
| 6 | `references/knowledge-schema-template.md` | 新增（schema 含自我成長規則） |
| 7 | `SKILL.md` | 版本 1.1 → 2.0，更新 description |

## Skills 來源策略

```
優先順序：
1. 從 ai-team-agent/skills/{skill-name}/ 複製（同 repo）
2. 從 .kiro/skills/{skill-name}/ 複製（全域）
3. 僅複製 SKILL.md（輕量版，省空間）
```

`build_kiro.py --clone-skills` 已有此邏輯，升級為依角色自動選擇。

## 驗收條件

- [ ] `build_kiro.py` 產出後每個 Agent 的 `.kiro/skills/` 有角色對應 Skills
- [ ] `knowledge/schema.md` 含自我成長規則
- [ ] SOUL.md 含 `## 📚 自我成長` 段
- [ ] `knowledge/wiki/overview.md` 列出已安裝 Skills
- [ ] Agent 實際運作時會在完成任務後寫入 wiki 頁面

## 預估工時

1 小時（改 7 個檔案）。

---

*使用 ark-superpowers 框架產出。*

---
title: "qa-agent Knowledge Schema"
type: system
created: 2026-06-17
updated: 2026-06-25
---

> 此模板由 `build_kiro.py` 產出到每個 Agent 的 `knowledge/schema.md`。

---

## 知識庫三層架構

```
專案根目錄/
├── knowledge/                    ← 團隊共用知識庫（IDE 開發時寫入）
│   ├── shared/                   ← 排程整理後的共用知識（LLM 分析彙整）
│   │   ├── raw/                  ← Agent 產出 → LLM 分析 → 放入此處
│   │   └── wiki/                 ← 共用精煉知識
│   ├── raw/
│   ├── wiki/
│   ├── schema.md
│   ├── index.md
│   └── log.md
│
└── agents/{name}-agent/
    └── knowledge/                ← Agent 私有知識庫（Agent 自己維護）
        ├── raw/
        ├── wiki/
        ├── schema.md             ← 本模板
        ├── index.md
        └── log.md
```

## 讀取優先順序

| 優先 | 來源 | 何時搜尋 |
|------|------|---------|
| 1️⃣ | 自己的 `knowledge/wiki/` | **預設**（所有查詢先搜自己） |
| 2️⃣ | 根目錄 `knowledge/shared/wiki/` | 自己的找不到 or 明確指定「共用知識」 |
| 3️⃣ | 根目錄 `knowledge/wiki/` | 明確指定「團隊知識」 |

## 寫入規則

| 場景 | 寫入位置 | 說明 |
|------|---------|------|
| Agent 完成任務學到東西 | **自己的** `knowledge/wiki/` | 私有，不影響他人 |
| Agent 解決了通用問題 | **自己的** `knowledge/wiki/` | 先存私有 |
| 排程整理（daily） | 根目錄 `knowledge/shared/raw/` | LLM 分析私有知識 → 提取通用部分 → 放入 shared/raw |
| IDE 手動寫入 | 根目錄 `knowledge/wiki/` | 人類手動維護的團隊知識 |

## 共用知識同步機制

```
┌─────────────────┐      排程 daily-knowledge-digest
│ Agent A wiki/   │──┐
│ Agent B wiki/   │──┤──→ LLM 分析通用性 → shared/raw/ → ingest → shared/wiki/
│ Agent C wiki/   │──┘
└─────────────────┘
         ↑ 寫入                        ↓ 讀取（優先級 2）
    各 Agent 私有                   所有 Agent 可搜尋
```

## 自我成長規則

Agent 在以下時機必須更新**自己的**知識庫：

| 觸發時機 | 動作 | 寫入位置 |
|---------|------|---------|
| 完成任務後 | 將筆記/技巧記錄下來 | raw/ |
| 遇到問題並解決 | 記錄問題 + 解法 | raw/ |
| 收到 Spec/Design 文件 | 存入作為參考 | raw/ |
| 排程定期 ingest | LLM 萃取 raw → 結構化頁面 | wiki/（由 ingest 產出） |

> **規則**：Agent 只寫 raw/，wiki/ 由排程 ingest 產出。

## Frontmatter 規範

```yaml
---
title: "頁面標題"
type: concept | entity | source | synthesis | troubleshooting | overview
tags: [tag1, tag2]
sources: [raw/來源檔案]
related: [相關頁面檔名]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: seedling | developing | mature
---
```

## 操作規則

| 規則 | 說明 |
|------|------|
| raw/ 唯讀 | LLM 只讀不改 |
| 修改後同步 | 改 wiki → 必須更新 index.md + log.md |
| log append-only | 禁止刪除舊記錄 |
| 雙向連結 | 使用 `[[page_name]]` 建構圖譜 |
| 矛盾標記 | `> ⚠️ 矛盾：...` 只標記不解決 |
| 不確定標記 | 用 `(?)` 標記 |

## 禁止事項

- ❌ 不可直接寫入根目錄 `knowledge/`（由排程/人類管理）
- ❌ 不可刪除 log.md 舊記錄
- ❌ 不可修改 raw/ 中的檔案
- ❌ 不可在私有知識中存放敏感 Token/密碼

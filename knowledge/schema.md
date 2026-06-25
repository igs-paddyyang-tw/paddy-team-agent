---
title: "共用知識庫 Schema"
type: system
created: 2026-06-17
updated: 2026-06-25
---

# 共用知識庫 Schema v3.1

## 定位

此為專案根目錄的共用知識庫，所有 Agent 可讀取，不可直接寫入 wiki/。

## 目錄結構

```
knowledge/
├── raw/          → 所有輸入都先進這裡（人類 + 排程 LLM）
├── wiki/         → 由 LLM ingest 萃取產出（不可手動直接寫入）
├── schema.md     → 本文件
├── index.md      → 索引目錄
└── log.md        → 操作日誌（append-only）
```

## 寫入規則

| 誰 | 寫到哪 | 流程 |
|----|--------|------|
| 人類（IDE） | `raw/` | 放入文件 → LLM ingest → 自動產出 wiki/ |
| 排程 LLM | `raw/` | 分析 Agent 私有知識 → 提取通用部分 → 放入 raw/ |
| LLM ingest | `wiki/` | raw/ 萃取 → 結構化頁面（唯一寫入 wiki 的方式） |
| Agent ❌ | — | 禁止直接寫入根目錄 knowledge/ |

## 讀取規則

所有 Agent 以優先級 2 搜尋此知識庫（優先級 1 是自己的 knowledge/）。

## 操作規則

| 規則 | 說明 |
|------|------|
| raw/ 為輸入口 | 所有新知識先進 raw/，由 LLM 萃取到 wiki/ |
| wiki/ 不可手動寫 | 只能透過 ingest 流程產出 |
| 修改後同步 | wiki 變動 → 更新 index.md + log.md |
| log append-only | 禁止刪除舊記錄 |

## Frontmatter 規範

```yaml
---
title: "頁面標題"
type: concept | entity | source | synthesis | troubleshooting | overview
tags: [tag1, tag2]
sources: [raw/來源檔案]
related: [相關頁面]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: seedling | developing | mature
---
```

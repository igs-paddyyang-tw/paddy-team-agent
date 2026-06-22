---
title: "team Knowledge Schema"
type: system
created: 2026-06-17
updated: 2026-06-17
---

# Wiki Schema v3.0

## 目錄結構

```
knowledge/
├── raw/          → 唯讀原始資料
├── wiki/         → 結構化知識頁面
├── schema.md     → 本文件
├── index.md      → 索引目錄
└── log.md        → 操作日誌（append-only）
```

## Frontmatter（必要）

```yaml
---
title: "頁面標題"
type: concept | entity | source | synthesis | overview
tags: [tag1, tag2]
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

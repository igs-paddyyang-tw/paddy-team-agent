---
title: "共用知識庫 Schema"
type: system
created: 2026-06-25
updated: 2026-06-25
---

# 共用知識庫 Schema

## 來源

此目錄的知識由排程 LLM 從各 Agent 私有知識庫分析彙整而來。

## 流程

```
各 Agent knowledge/wiki/ → 排程分析 → shared/raw/ → ingest → shared/wiki/
```

## 規則

- `raw/` 由排程 LLM 寫入（Agent 私有知識的通用化版本）
- `wiki/` 由 ingest 後產出
- 所有 Agent 可讀取，不可直接寫入
- 人類可手動修改/刪除

---
title: "coder-agent 知識庫概覽"
type: overview
tags: [overview, coder]
created: 2026-06-17
updated: 2026-07-08
---

# coder-agent 知識庫

本知識庫包含 coder-agent 的核心開發規範與 best practices，涵蓋 Python/FastAPI 後端開發全流程。

## 📚 知識頁面

| 頁面 | 主題 | 狀態 |
|------|------|------|
| [[python-fastapi-standards]] | 專案結構、命名規則、Error Handling、Middleware | 🌳 mature |
| [[api-design-conventions]] | RESTful 命名、版本控制、Pagination、Error Response | 🌳 mature |
| [[database-design]] | 正規化、索引策略、Migration 流程、查詢優化 | 🌳 mature |
| [[code-review-checklist]] | 安全性、效能、可讀性、測試覆蓋 | 🌳 mature |

## 🔗 知識關聯圖

```
python-fastapi-standards ←→ api-design-conventions
        ↕                           ↕
code-review-checklist    ←→  database-design
```

## 📝 使用指引

- 開發新功能前：參考 `python-fastapi-standards` 確認架構
- 設計 API 時：依循 `api-design-conventions` 定義端點
- DB 設計/優化：查閱 `database-design` 索引與 migration 策略
- 提 PR 前：逐項檢查 `code-review-checklist`

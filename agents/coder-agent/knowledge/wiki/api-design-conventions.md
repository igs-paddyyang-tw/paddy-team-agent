---
title: "API 設計慣例"
type: concept
tags: [api, rest, design, conventions]
related: [python-fastapi-standards, database-design]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# API 設計慣例

## RESTful 命名原則

| 操作 | Method | Path | 說明 |
|------|--------|------|------|
| 列表 | GET | `/api/v1/users` | 複數名詞，無動詞 |
| 取得 | GET | `/api/v1/users/{id}` | Path param 用資源 ID |
| 建立 | POST | `/api/v1/users` | Body 帶完整資源 |
| 更新 | PUT | `/api/v1/users/{id}` | 完整取代 |
| 部分更新 | PATCH | `/api/v1/users/{id}` | 僅送變更欄位 |
| 刪除 | DELETE | `/api/v1/users/{id}` | 回傳 204 No Content |

**命名規則**：
- 路徑一律小寫、複數名詞：`/orders`, `/order-items`（kebab-case）
- 巢狀資源最多兩層：`/users/{id}/orders`，超過改用 query filter
- 動作型端點用 POST + 動詞：`POST /api/v1/reports/generate`

## 版本控制

```
/api/v1/users    ← URL path versioning（首選）
/api/v2/users    ← 破壞性變更時升版
```

- 使用 URL path versioning（`/api/v1/`），不用 header versioning
- 非破壞性變更（新增欄位、新增 endpoint）不升版
- 破壞性變更（移除欄位、改型別、改語意）必須升版
- 舊版 API 至少維護 6 個月 deprecation period

## Pagination

```json
// Request
GET /api/v1/users?page=2&page_size=20&sort=-created_at

// Response
{
  "data": [...],
  "pagination": {
    "page": 2,
    "page_size": 20,
    "total_count": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
  }
}
```

| 參數 | 預設 | 上限 | 說明 |
|------|------|------|------|
| page | 1 | — | 頁碼，從 1 開始 |
| page_size | 20 | 100 | 每頁筆數 |
| sort | `-created_at` | — | 前綴 `-` 為降序 |

- 大資料集（>10萬筆）改用 cursor-based pagination
- Cursor 格式：`?cursor=eyJpZCI6MTIzfQ&limit=20`

## Error Response 格式

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "reason": "invalid_format",
        "message": "Email format is invalid"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

**HTTP Status Code 使用**：

| Code | 用途 |
|------|------|
| 200 | 成功（有 body） |
| 201 | 建立成功 |
| 204 | 成功（無 body，如 DELETE） |
| 400 | 參數驗證錯誤 |
| 401 | 未認證 |
| 403 | 無權限 |
| 404 | 資源不存在 |
| 409 | 衝突（如重複建立） |
| 422 | 業務邏輯錯誤 |
| 429 | Rate limit |
| 500 | 伺服器內部錯誤 |

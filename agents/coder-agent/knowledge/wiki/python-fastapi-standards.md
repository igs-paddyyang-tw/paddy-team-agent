---
title: "Python/FastAPI 開發規範"
type: concept
tags: [python, fastapi, standards, architecture]
related: [api-design-conventions, code-review-checklist]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# Python/FastAPI 開發規範

## 專案結構

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app 實例 + lifespan
│   ├── config.py            # pydantic-settings 配置
│   ├── dependencies.py      # 共用 Depends
│   ├── routers/             # 路由模組（一個 domain 一個檔案）
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   ├── models/              # SQLAlchemy / Pydantic models
│   ├── schemas/             # Request/Response schemas
│   ├── services/            # Business logic 層
│   ├── repositories/        # DB 存取層（Repository Pattern）
│   └── middleware/          # 自訂 middleware
├── migrations/              # Alembic migrations
├── tests/
├── pyproject.toml
└── Dockerfile
```

## 命名規則

| 類別 | 風格 | 範例 |
|------|------|------|
| 模組/檔案 | snake_case | `user_service.py` |
| 類別 | PascalCase | `UserRepository` |
| 函式/變數 | snake_case | `get_user_by_id` |
| 常數 | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| Router prefix | 複數名詞 | `/api/v1/users` |
| Pydantic Schema | 動詞+名詞 | `CreateUserRequest`, `UserResponse` |

## Error Handling

```python
# 自訂例外階層
class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource}_not_found", f"{resource} {id} not found", 404)

# 全域例外處理器
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status, content={
        "error": {"code": exc.code, "message": exc.message}
    })
```

- 所有預期錯誤使用 `AppError` 子類，禁止直接 raise `HTTPException`（除非極簡場景）
- 未預期錯誤由全域 500 handler 捕獲，log full traceback，回傳通用訊息

## Middleware 規範

| 順序 | Middleware | 用途 |
|------|-----------|------|
| 1 | CORSMiddleware | 跨域設定 |
| 2 | RequestIdMiddleware | 注入 X-Request-ID |
| 3 | LoggingMiddleware | 記錄 method/path/duration |
| 4 | AuthMiddleware | Token 驗證（需要時） |

- Middleware 順序：外層先執行，內層後執行（洋蔥模型）
- 效能敏感路徑（health check）應在 Middleware 前短路
- 使用 `app.add_middleware()` 而非 decorator，方便測試時替換

---
title: "DB Schema 設計原則"
type: concept
tags: [database, schema, migration, optimization]
related: [python-fastapi-standards, api-design-conventions]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# DB Schema 設計原則

## 正規化原則

| 等級 | 規則 | 實務建議 |
|------|------|---------|
| 1NF | 每欄位原子值 | JSON 欄位例外：僅用於非查詢的 metadata |
| 2NF | 消除部分依賴 | 複合 PK 場景務必檢查 |
| 3NF | 消除遞移依賴 | **生產環境標準**，大多數表停在此 |
| 反正規化 | 效能需求 | 明確標註原因，加註 `-- denormalized: reason` |

**命名規範**：
- 表名：複數、snake_case → `user_orders`
- 欄位：snake_case → `created_at`, `order_status`
- 外鍵：`{referenced_table_singular}_id` → `user_id`
- 索引：`ix_{table}_{columns}` → `ix_orders_user_id_created_at`
- 唯一約束：`uq_{table}_{columns}` → `uq_users_email`

## 索引策略

```sql
-- 必建索引
CREATE INDEX ix_orders_user_id ON orders(user_id);              -- FK
CREATE INDEX ix_orders_status_created ON orders(status, created_at); -- 複合查詢

-- 覆蓋索引（避免回表）
CREATE INDEX ix_orders_covering ON orders(user_id, status, total) INCLUDE (created_at);

-- 部分索引（減少索引大小）
CREATE INDEX ix_orders_active ON orders(created_at) WHERE status = 'active';
```

**索引決策原則**：
1. WHERE/JOIN/ORDER BY 欄位優先建索引
2. 選擇性低的欄位（如 boolean）不單獨建索引，搭配高選擇性欄位組複合索引
3. 複合索引遵循**最左前綴原則**，高選擇性欄位放前面
4. 單表索引數量 ≤ 5，超過需 review 合理性
5. 定期檢查未使用索引並清理

## Migration 流程

```bash
# 建立 migration
alembic revision --autogenerate -m "add_user_preferences_table"

# 檢查 SQL（上線前必看）
alembic upgrade head --sql

# 執行 migration
alembic upgrade head

# 回滾
alembic downgrade -1
```

**規則**：
- 每個 migration 必須可 rollback（提供 downgrade）
- 大表 DDL（加欄位、建索引）使用 `CONCURRENTLY`（PostgreSQL）
- 禁止在 migration 中執行大量 DML（拆成 data migration script）
- Migration 命名格式：`{revision}_描述.py`（Alembic 自動生成 revision ID）
- 上線前在 staging 跑過 upgrade + downgrade 完整流程

## 查詢優化

| 問題 | 解法 |
|------|------|
| N+1 查詢 | 使用 `joinedload` / `selectinload`（SQLAlchemy） |
| 大量 COUNT | 改用近似值或快取 |
| OFFSET 分頁慢 | 改用 keyset pagination（`WHERE id > ?`） |
| 全表掃描 | 檢查索引、加 LIMIT |
| Lock 競爭 | 使用 `SELECT FOR UPDATE SKIP LOCKED` |

**效能基準**：
- 單一 API 查詢 ≤ 3 次 DB round-trip
- 單一查詢執行時間 < 100ms（P95）
- 批量寫入使用 `bulk_insert_mappings` 或 `COPY`
- 讀寫分離：報表查詢走 read replica

## 必備欄位模板

```sql
CREATE TABLE example (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- business fields here --
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ          -- soft delete
);

-- 自動更新 updated_at trigger
CREATE TRIGGER set_updated_at BEFORE UPDATE ON example
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
```

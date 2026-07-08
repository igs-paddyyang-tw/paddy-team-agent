---
title: "程式碼 Review Checklist"
type: concept
tags: [code-review, security, performance, quality]
related: [python-fastapi-standards, api-design-conventions, database-design]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# 程式碼 Review Checklist

## 🔒 安全性

- [ ] **SQL Injection**：所有 DB 查詢使用參數化（ORM 或 parameterized query）
- [ ] **Input Validation**：所有外部輸入經 Pydantic schema 驗證，拒絕未知欄位
- [ ] **Authentication**：敏感端點有正確的認證 middleware
- [ ] **Authorization**：資源存取有權限檢查（不只靠認證）
- [ ] **Secrets**：無硬編碼密鑰/Token，全部走環境變數或 secret manager
- [ ] **CORS**：允許的 origin 明確列舉，非 `*`（生產環境）
- [ ] **Rate Limiting**：公開 API 有速率限制
- [ ] **Log 安全**：不記錄密碼、Token、PII 等敏感資訊
- [ ] **Dependency**：新增依賴已檢查 CVE，版本 pinned

## ⚡ 效能

- [ ] **N+1 查詢**：ORM 關聯載入使用 eager loading 或批量查詢
- [ ] **索引**：新增的 WHERE/JOIN 欄位已確認有對應索引
- [ ] **分頁**：列表 API 有分頁，單次回傳上限 ≤ 100
- [ ] **快取**：高頻讀取、低變更資料有快取策略
- [ ] **Async**：I/O bound 操作使用 async（DB、HTTP call、file）
- [ ] **Batch**：批量操作使用 bulk API，避免迴圈逐筆處理
- [ ] **Connection Pool**：DB/Redis 連線池大小合理，有超時設定
- [ ] **Payload Size**：Response 不回傳不必要欄位，大物件用 streaming

## 📖 可讀性

- [ ] **命名**：函式/變數名稱自解釋，符合團隊命名規則
- [ ] **單一職責**：每個函式/類別只做一件事，函式 ≤ 30 行
- [ ] **註解**：複雜邏輯有 WHY 註解（不是 WHAT）
- [ ] **Type Hints**：所有公開函式有完整 type annotation
- [ ] **Magic Number**：無魔法數字，抽成具名常數
- [ ] **Dead Code**：無註解掉的程式碼、無用 import
- [ ] **一致性**：風格與現有 codebase 一致（linter 通過）
- [ ] **Error Message**：錯誤訊息對除錯有幫助，包含 context

## 🧪 測試覆蓋

- [ ] **Happy Path**：主要成功路徑有測試
- [ ] **Edge Cases**：邊界值、空值、極端輸入有覆蓋
- [ ] **Error Path**：預期錯誤情境有測試（4xx 回傳）
- [ ] **Integration**：API 端點有 integration test（TestClient）
- [ ] **Mock 範圍**：只 mock 外部依賴，不 mock 被測邏輯
- [ ] **Assertion**：每個測試有明確 assertion，不只「不報錯」
- [ ] **獨立性**：測試之間無順序依賴，可平行執行
- [ ] **覆蓋率**：新增程式碼覆蓋率 ≥ 80%，核心邏輯 ≥ 90%

## 📋 Review 流程

1. **Self Review**：提 PR 前自己過一遍此 checklist
2. **CI Green**：lint + test + type check 全過才 request review
3. **Small PR**：單一 PR ≤ 400 行變更，超過拆分
4. **描述完整**：PR description 說明 what/why/how + 測試方式
5. **回應**：reviewer 提出的問題 24hr 內回覆

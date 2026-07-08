---
title: "Code Review 指南"
type: concept
tags: [code-review, quality, security, best-practices]
related: [testing-strategy, cicd-quality-gates]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# Code Review 指南

## Review 重點（優先順序）

| 優先級 | 審查面向 | 說明 |
|--------|---------|------|
| P0 | 安全性 | 注入攻擊、認證繞過、敏感資訊洩漏 |
| P1 | 正確性 | 邏輯錯誤、邊界條件、錯誤處理 |
| P2 | 可維護性 | 命名清晰、職責單一、適當抽象 |
| P3 | 效能 | 不必要的迴圈、N+1 查詢、記憶體洩漏 |
| P4 | 風格 | 格式一致性（由 linter 自動處理為主） |

## 常見問題模式

### 🚨 必須修改（Blocker）

- **硬編碼密鑰/Token**：任何出現在程式碼中的 secret
- **SQL/NoSQL Injection**：未參數化的查詢
- **未驗證的使用者輸入**：直接使用 request body 無 validation
- **錯誤的錯誤處理**：bare `except:`、吞掉 exception
- **競態條件**：共享狀態無鎖保護
- **無限迴圈/遞迴**：缺少終止條件

### ⚠️ 建議修改（Warning）

- **過長函式**：單一函式超過 50 行
- **深度巢狀**：超過 3 層 if/loop 嵌套
- **重複程式碼**：相同邏輯出現 3 次以上
- **魔術數字**：未命名的常數值
- **缺少型別提示**：公開 API 未標註 type hints
- **TODO 無追蹤**：未關聯 issue 的 TODO 註解

### 💡 可選改善（Nit）

- 命名可以更精確
- 可以抽取為獨立函式提升可讀性
- 文件字串可以更完整

## 安全審計項目

### 認證與授權
- [ ] API 端點是否有適當的認證檢查
- [ ] 權限控制是否在 server side 實施
- [ ] JWT/Token 是否有過期機制
- [ ] 敏感操作是否有額外驗證

### 資料處理
- [ ] 使用者輸入是否經過 sanitization
- [ ] 輸出是否有 XSS 防護（HTML escape）
- [ ] 檔案上傳是否限制類型和大小
- [ ] 敏感資料是否加密儲存

### 依賴安全
- [ ] 新增依賴是否為已知安全版本
- [ ] 是否有已知 CVE 漏洞
- [ ] 依賴是否使用 pinned version

## Review 流程規範

1. **PR 大小**：單一 PR 不超過 400 行變更（不含測試）
2. **回應時限**：收到 Review 請求後 4 小時內開始 Review
3. **修改回覆**：每個 comment 需明確標記 resolved 或 won't fix（附理由）
4. **合併條件**：至少 1 個 Approve + CI 全過 + 無未解決 Blocker

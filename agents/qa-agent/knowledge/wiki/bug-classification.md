---
title: "Bug 分類標準"
type: concept
tags: [bug, severity, priority, regression, classification]
related: [testing-strategy, cicd-quality-gates]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# Bug 分類標準

## Severity 嚴重度定義（P0-P3）

| 等級 | 名稱 | 定義 | 範例 |
|------|------|------|------|
| **P0** | Critical | 系統完全不可用，影響所有使用者，無 workaround | 服務崩潰、資料遺失、安全漏洞被利用 |
| **P1** | High | 核心功能異常，影響大量使用者，workaround 困難 | 登入失敗、支付錯誤、主流程阻斷 |
| **P2** | Medium | 非核心功能異常，影響部分使用者，有 workaround | 匯出格式錯誤、非關鍵頁面顯示異常 |
| **P3** | Low | 輕微問題，不影響功能使用 | UI 文字錯誤、排版微調、非必要提示缺失 |

## Priority 處理優先級

| Priority | 對應情境 | 說明 |
|----------|---------|------|
| Immediate | P0 + 生產環境 | 立即處理，所有人停下手邊工作 |
| High | P1 或 P0 非生產 | 當前 Sprint 內修復 |
| Medium | P2 | 排入下個 Sprint |
| Low | P3 | 排入 Backlog，有空處理 |

> **注意**：Priority 可根據業務影響調整。例如 P3 bug 若影響 VIP 客戶，可提升 Priority。

## 修復時限（SLA）

| Severity | 回應時間 | 修復時限 | 驗證時限 |
|----------|---------|---------|---------|
| P0 | 15 分鐘 | 4 小時 | 修復後立即 |
| P1 | 1 小時 | 24 小時 | 修復後 2 小時內 |
| P2 | 4 小時 | 7 天 | 下次部署前 |
| P3 | 1 工作天 | 30 天 | 下次 Sprint Review |

### P0 處理流程

1. **回應**：值班人員 15 分鐘內 acknowledge
2. **評估**：確認影響範圍，決定 hotfix 或 rollback
3. **修復**：開 hotfix branch，最小化修改
4. **驗證**：QA 立即驗證，確認不引入新問題
5. **部署**：走加速部署流程（跳過非必要 gate）
6. **事後**：24 小時內產出 post-mortem 報告

## 回歸測試規則

### 何時觸發回歸測試

| 情境 | 回歸測試範圍 |
|------|------------|
| P0/P1 hotfix | 完整回歸（所有 critical path） |
| P2 修復 | 相關模組回歸 |
| P3 修復 | 修改檔案的單元測試 |
| Release 前 | 完整回歸 + E2E |

### 回歸測試規範

1. **Bug 修復必須附帶測試**：每個 bug fix 至少新增 1 個 test case 覆蓋該場景
2. **回歸套件維護**：新增的 bug test case 永久納入回歸套件
3. **自動化優先**：回歸測試必須可自動化執行
4. **不可跳過**：回歸測試失敗 = 阻擋部署（同 CI Gate 規則）

### 回歸測試命名

```
test_regression_{issue_id}_{簡短描述}
```

範例：`test_regression_BUG123_login_timeout_on_slow_network`

## Bug 生命週期

```
New → Confirmed → In Progress → Fixed → Verified → Closed
                                  ↓                   ↓
                              Won't Fix          Reopened → In Progress
```

## 分類決策樹

```
系統能正常使用嗎？
├── 否 → 所有使用者？ → 是 → P0
│                      → 否 → P1
└── 是 → 核心功能受影響？ → 是 → P2
                           → 否 → P3
```

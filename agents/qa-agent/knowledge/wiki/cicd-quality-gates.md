---
title: "CI/CD 品質門檻"
type: concept
tags: [cicd, quality-gate, lint, coverage, security-scan, pipeline]
related: [testing-strategy, code-review-guide]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# CI/CD 品質門檻

## Pipeline 階段與品質門檻

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Lint    │───→│  Build   │───→│  Test    │───→│ Security │───→│  Deploy  │
│  Gate    │    │  Gate    │    │  Gate    │    │  Gate    │    │  Gate    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

每個 Gate 失敗 → Pipeline 中止 → 通知開發者修復

## Gate 1: Lint Pass

| 工具 | 檢查項目 | 失敗條件 |
|------|---------|---------|
| `ruff` | Python 程式碼風格 + 常見錯誤 | 任何 error 等級 |
| `mypy` | 型別檢查 | 任何 type error |
| `eslint` | JavaScript/TypeScript 風格 | 任何 error（warning 允許） |
| `prettier` | 格式化一致性 | 有未格式化的檔案 |
| `markdownlint` | 文件格式 | 結構性錯誤 |

**規則**：0 tolerance for lint errors。Warning 記錄但不阻擋。

## Gate 2: Build Pass

- 所有語言的編譯/轉譯必須成功
- Docker image 必須能成功 build
- 不允許 deprecated API 的 build warning（逐步啟用）

## Gate 3: Test Pass + Coverage ≥ 80%

| 指標 | 門檻值 | 說明 |
|------|--------|------|
| 單元測試通過率 | 100% | 任何失敗即阻擋 |
| 整合測試通過率 | 100% | 任何失敗即阻擋 |
| 整體 Line Coverage | ≥ 80% | 低於即阻擋合併 |
| 新增程式碼 Coverage | ≥ 85% | 新 code 要求更高 |
| Branch Coverage | ≥ 70% | 確保分支邏輯被測試 |

**工具**：`pytest-cov`（Python）、`jest --coverage`（JS/TS）

**例外處理**：
- 若因正當理由無法達標，需在 PR 中標記 `coverage-exception` 並附理由
- 例外需至少 2 位 reviewer approve

## Gate 4: Security Scan

| 工具 | 掃描範圍 | 阻擋條件 |
|------|---------|---------|
| `trivy` | 容器映像漏洞 | Critical / High 漏洞 |
| `bandit` | Python 安全問題 | High confidence issue |
| `npm audit` | Node.js 依賴漏洞 | Critical severity |
| `gitleaks` | 程式碼中的 secrets | 任何洩漏 |
| `OWASP ZAP` | API 安全（staging） | High risk alert |

**規則**：
- Critical/High 漏洞必須修復後才能合併
- Medium 漏洞需建立追蹤 issue，限期 7 天修復
- Low 漏洞記錄即可，排入 backlog

## Gate 5: Deploy Gate（僅 production）

- Staging 環境 smoke test 通過
- 無 P0/P1 open bugs
- Release notes 已更新
- Rollback plan 已確認

## 失敗處理流程

1. Pipeline 失敗 → Slack/Teams 通知開發者
2. 開發者 30 分鐘內確認（acknowledge）
3. 修復後重新觸發 Pipeline
4. 連續失敗 3 次 → 升級至 Tech Lead 介入

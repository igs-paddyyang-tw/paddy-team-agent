---
title: "qa-agent 概覽"
type: overview
tags: [overview, qa, testing, quality]
created: 2026-06-17
updated: 2026-07-08
---

# QA Agent 知識庫概覽

QA Agent 負責軟體品質保證的全流程管控，涵蓋測試策略、程式碼審查、CI/CD 品質門檻與 Bug 管理。

## 📚 知識頁面

| 頁面 | 說明 | 狀態 |
|------|------|------|
| [[testing-strategy]] | 測試金字塔分層、覆蓋率目標、Mock 策略 | mature |
| [[code-review-guide]] | Review 重點、常見問題模式、安全審計 | mature |
| [[cicd-quality-gates]] | Pipeline 各階段品質門檻定義 | mature |
| [[bug-classification]] | Severity P0-P3、修復 SLA、回歸測試規則 | mature |

## 🎯 核心職責

1. **測試規劃**：根據 [[testing-strategy]] 確保各層測試覆蓋
2. **程式碼審查**：依循 [[code-review-guide]] 執行安全與品質審計
3. **品質守門**：維護 [[cicd-quality-gates]] 確保 Pipeline 品質標準
4. **Bug 管理**：按 [[bug-classification]] 標準分類、追蹤與驗證修復

## 🔗 知識圖譜

```
testing-strategy ←→ cicd-quality-gates
       ↕                    ↕
bug-classification ←→ code-review-guide
```

四個頁面互相關聯，構成 QA Agent 完整的品質保證知識體系。

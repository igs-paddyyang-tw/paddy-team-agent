---
title: "測試策略"
type: concept
tags: [testing, unit-test, integration-test, e2e, coverage, mock]
related: [cicd-quality-gates, bug-classification]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# 測試策略

## 測試金字塔分層

| 層級 | 類型 | 佔比 | 執行速度 | 維護成本 |
|------|------|------|---------|---------|
| L1 | 單元測試 (Unit) | 70% | < 5ms/case | 低 |
| L2 | 整合測試 (Integration) | 20% | < 500ms/case | 中 |
| L3 | 端對端測試 (E2E) | 10% | < 30s/case | 高 |

## 單元測試規範

- **範圍**：單一函式/方法，隔離所有外部依賴
- **命名規則**：`test_{功能}_{情境}_{預期結果}`
- **原則**：每個 test case 只驗證一個行為
- **必須覆蓋**：核心業務邏輯、邊界條件、錯誤處理路徑
- **禁止**：存取真實 DB / 網路 / 檔案系統

## 整合測試規範

- **範圍**：模組間互動、API 端點、DB 操作
- **環境**：使用 Docker Compose 啟動依賴服務（MongoDB、Redis）
- **資料策略**：每個 test suite 前 setup、後 teardown，禁止跨 suite 共享狀態
- **重點場景**：API 合約驗證、DB transaction 正確性、外部服務互動

## E2E 測試規範

- **範圍**：完整使用者流程（登入→操作→驗證結果）
- **工具**：Playwright（Web）、pytest + requests（API flow）
- **數量控制**：僅覆蓋 critical path，不超過 20 個 scenarios
- **失敗容忍**：允許重試 1 次（處理 flaky test）

## 覆蓋率目標

| 指標 | 目標 | 硬門檻 |
|------|------|--------|
| Line Coverage | ≥ 85% | ≥ 80%（CI 不過） |
| Branch Coverage | ≥ 75% | ≥ 70% |
| 新增程式碼覆蓋率 | ≥ 90% | ≥ 85% |

## Mock 策略

| 場景 | Mock 方式 | 說明 |
|------|----------|------|
| 外部 API | `responses` / `httpx_mock` | 模擬 HTTP 回應 |
| 資料庫 | `mongomock` / in-memory SQLite | 單元測試用 |
| 時間相關 | `freezegun` | 固定時間避免 flaky |
| 訊息佇列 | fake broker | 模擬 publish/consume |
| 檔案系統 | `tmp_path` fixture | pytest 內建 |

### Mock 原則

1. **只在單元測試 Mock**：整合測試盡量用真實服務
2. **Mock 邊界在模組外**：不要 Mock 自己模組內的函式
3. **驗證互動**：Mock 物件需 assert 呼叫次數和參數
4. **保持同步**：外部 API 變更時，同步更新 Mock 定義

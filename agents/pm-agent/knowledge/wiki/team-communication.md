---
title: "團隊溝通規範"
type: concept
tags: [communication, team, protocol, messaging]
sources: []
related: [task-dispatch-rules, acceptance-criteria-template]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# 團隊溝通規範

定義 Agent 團隊間的訊息格式、回報時機、升級路徑和完成標記。

---

## 訊息格式（Message Format）

所有 Agent 間通訊使用統一前綴標籤：

| 標籤 | 用途 | 範例 |
|------|------|------|
| `[DISPATCH]` | PM 派工 | `[DISPATCH] TASK-001 → dev-agent` |
| `[ACK]` | Agent 確認收到 | `[ACK] TASK-001 已接收，預估 15 分鐘` |
| `[PROGRESS]` | 進度回報 | `[PROGRESS] TASK-001: 3/5 AC 完成` |
| `[BLOCKED]` | 阻塞通知 | `[BLOCKED] TASK-001: 等待 TASK-002 產出` |
| `[DONE]` | 完成回報 | `[DONE] TASK-001: 全部 AC 通過` |
| `[FAILED]` | 失敗回報 | `[FAILED] TASK-001: AC-3 無法滿足，原因...` |
| `[REVIEW]` | 請求審核 | `[REVIEW] TASK-001 請 PM 驗收` |
| `[ESCALATE]` | 升級請求 | `[ESCALATE] 循環依賴無法解決，需使用者決策` |

### 訊息結構

```
[標籤] TASK-ID: 簡述
---
詳細內容（選填）
- 要點 1
- 要點 2
```

---

## 回報時機（Reporting Triggers）

| 事件 | 必須回報 | 時限 |
|------|---------|------|
| 收到派工 | `[ACK]` | 30 秒內 |
| 完成 25% / 50% / 75% | `[PROGRESS]` | 即時 |
| 遇到阻塞 | `[BLOCKED]` | 即時 |
| 任務完成 | `[DONE]` + `[REVIEW]` | 即時 |
| 無法完成 | `[FAILED]` | 即時 + 原因說明 |
| 靜默超過 5 分鐘 | PM 發送 ping | 自動 |

**原則**：寧可多報不可少報。不確定是否需要回報時，就回報。

---

## 升級路徑（Escalation Path）

```
Level 0: Agent 自行解決
   ↓ 無法解決
Level 1: 回報 PM Agent，PM 協調其他 Agent 協助
   ↓ 團隊無法解決
Level 2: PM 向使用者升級，提供問題描述 + 已嘗試方案
   ↓ 使用者無回應
Level 3: 暫停任務，記錄於 log，等待下次互動
```

### 升級條件

| 狀態 | 升級判斷 |
|------|---------|
| 技術阻塞 | 嘗試 2 種方案均失敗 |
| 需求不明 | 釐清問題 2 次未獲回應 |
| 資源不足 | 所有可用 Agent 負載已滿 |
| 權限問題 | 需要 Agent 不具備的存取權 |

---

## [DONE] 標記規範

`[DONE]` 是任務生命週期的終止信號，使用規則：

1. **僅在全部 AC 通過後**才可標記 `[DONE]`
2. `[DONE]` 訊息必須附帶驗證摘要
3. PM 確認後任務才真正關閉
4. 部分完成**不可**使用 `[DONE]`，應使用 `[PROGRESS]`

### [DONE] 訊息範例

```
[DONE] TASK-001: 使用者登入功能
---
驗證結果：
- ✅ AC-1: 有效帳密可登入
- ✅ AC-2: 無效密碼顯示錯誤訊息
- ✅ AC-3: 連續 5 次失敗鎖定帳號
品質門檻：lint 0 warning, 測試覆蓋 85%
```

---

## 禁止事項

- ❌ 不可跳過 `[ACK]` 直接開工（PM 無法追蹤狀態）
- ❌ 不可在 `[DONE]` 後繼續修改已交付的產出
- ❌ 不可使用自定義標籤（破壞解析一致性）
- ❌ 不可在升級訊息中省略已嘗試方案

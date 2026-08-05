---
description: 訊息路由 — 判斷意圖後自理或轉派 leader-agent
argument-hint: <使用者訊息>
---

收到以下訊息，判斷意圖並路由：

$ARGUMENTS

---

## 路由規則

- **分析／業務需求** → `send_to_instance("leader-agent", 訊息)`
- **服務問題／技術決策** → 自己處理
- **不確定** → 用編號選項詢問使用者意圖 `1️⃣ 2️⃣ 3️⃣`

最後用 `reply` 回報處理結果（≤ 150 字）。

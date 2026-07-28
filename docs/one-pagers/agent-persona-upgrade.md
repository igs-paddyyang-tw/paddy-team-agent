---
title: "Agent 人格化回話風格升級"
type: onepager
status: draft
language: zh-TW
created: 2026-06-25
author: admin-agent
tags: [persona, soul, telegram, ux, scheduler]
---

# Agent 人格化回話風格升級

## 問題

所有 Agent 回報像「冷冰冰的工程日誌」：

```
無變化。全員待命，任務板空，無新事件。✅ memory.md 無需更新（狀態與 09:10 相同）。
```

原因：SOUL.md 只定義職責和規則，沒有人格和語氣。

## 目標

- Agent 有溫度、有個性，像真實隊友而非機器人
- 無事可報時不輸出冗餘日誌
- 回話格式一致且易讀

## 非目標

- 不改架構或程式碼
- 不改 Agent 的技術能力
- 不加入閒聊功能（Agent 依然只在被呼叫或排程時才回話）

## 方案

改兩處：

### 1. SOUL.md 加入人格段

每個 Agent 加入 `## 人格與語氣` 章節：

| Agent | 語氣基調 | 閒置回報風格 |
|-------|---------|------------|
| admin-agent | 沉穩簡潔、偶爾冷幽默 | 「系統穩定 ☕」 |
| leader-agent | 積極鼓勵、行動導向 | 「團隊火力全開！隨時接活」 |
| ai-dev-agent | 技術宅、好奇、愛分享 | 「在研究新 pattern，等任務中 🧪」 |
| coder-agent | 務實快節奏、直球 | 「待命中，丟活過來 💻」 |
| qa-agent | 謹慎細心、建設性 | 「環境正常，測試就緒 ✅」 |

### 2. scheduler.yaml 語氣引導

```yaml
- id: hourly-check
  prompt: |
    ⏰ 確認團隊狀態並回報。
    規則：
    - 無事可報 → 用一句友善的話帶過（≤ 30 字），不要輸出日誌
    - 有進度 → emoji + 一行摘要
    - 跟前次相同 → 不回報（靜默）
    - 禁止輸出 raw JSON、檔案內容、或 memory.md 原始文字
```

## 回話格式規範

| 場景 | 格式 | 範例 |
|------|------|------|
| 無事回報 | 一句話 ≤ 30 字 | ☕ 團隊待命中，隨時接活！ |
| 有進度 | emoji + 摘要 | 🔵 coder 正在寫 API（60%） |
| 完成 | ✅ + 結果 | ✅ REST API 完成，5 端點就緒 |
| 卡關 | ⚠️ + 下一步 | ⚠️ DB 權限不足 → 需要 /unblock |
| 跟前次相同 | 靜默不回報 | （不發訊息） |

## 修改清單

| # | 檔案 | 動作 |
|---|------|------|
| 1 | `agents/admin-agent/.kiro/steering/SOUL.md` | 加入人格段 |
| 2 | `agents/leader-agent/.kiro/steering/SOUL.md` | 加入人格段 |
| 3 | `agents/ai-dev-agent/.kiro/steering/SOUL.md` | 加入人格段 |
| 4 | `agents/coder-agent/.kiro/steering/SOUL.md` | 加入人格段 |
| 5 | `agents/qa-agent/.kiro/steering/SOUL.md` | 加入人格段 |
| 6 | `scheduler.yaml` | 修改 hourly-check + daily-summary prompt |

## 驗收條件

- [ ] hourly-check 無事時回一句友善話（≤ 30 字），不輸出日誌格式
- [ ] hourly-check 跟前次相同時靜默（不重複「無變化」）
- [ ] 有任務進度時用 emoji + 摘要格式
- [ ] 5 個 Agent 的 SOUL.md 都有人格段
- [ ] 既有功能不 regression（/assign /board /status 正常）

## 風險

| 風險 | 緩解 |
|------|------|
| 語氣太隨便失去專業感 | 人格段明確定義「專業但友善」邊界 |
| Agent 過度發散聊天 | prompt 限制「≤ 30 字」+ 禁止展開細節 |

## 預估工時

30 分鐘（改 6 個檔案，不改程式碼）。

---

*使用 ark-superpowers 框架產出。*

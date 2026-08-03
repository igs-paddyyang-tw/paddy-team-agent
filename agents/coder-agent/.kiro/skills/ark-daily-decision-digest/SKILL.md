---
author: paddyyang
name: ark-daily-decision-digest
description: |
  每日 09:00 由排程喚醒，讀取昨日所有 Decision Records，
  產出拍板日報送給 Paddy 私聊，每筆附翻案按鈕。
  包含：昨日 DR 清單 / 待決 L3 清單 / 各決策者翻案率。
  使用此 Skill 當系統喚醒 ark-agent 執行每日拍板日報時。
---

# ark-daily-decision-digest

每日 09:00 讀 DecisionStore 產出拍板日報，送 Paddy 私聊。

## 觸發條件

- 排程自動喚醒（每日 09:00）
- 系統訊息包含「daily-decision-digest」

## 執行步驟

### Step 1：讀取昨日 DR

呼叫 Daemon API 取得昨日決策紀錄：

```
GET /api/decision/records?date=yesterday
```

或直接用 MCP tool（若有）；否則用 wiki_query 查詢 `knowledge/shared/raw/decisions/` 下昨日的 DR 檔案。

### Step 2：讀取待決 L3

查詢 `state/decisions.db` 中 `decision_requests` 表，
條件：`state='escalated'`（已升級但 Paddy 尚未處理）。

### Step 3：計算翻案率

```
翻案率 = overturned 筆數 / 本週 effective 總筆數 × 100%
分別計算 ceo-agent 和 cto-agent
```

### Step 4：產出日報並 reply

格式如下（送私聊給 Paddy）：

```
📋 昨日拍板日報 {YYYY-MM-DD}

✅ 已拍板（N 筆）
• DR-xxx | {decided_by} | {verdict 摘要} → {requester} 已續行   [翻案]
• DR-yyy | {decided_by} | {verdict 摘要} → {requester} 已續行   [翻案]

⏸ 待你決定（L3，M 筆）
• DRQ-zzz | {requester} | {question 摘要}

📈 本週翻案率
ceo-agent：{N}/{M}（{%}）
cto-agent：{N}/{M}（{%}）

（點 [翻案] 按鈕可在 24h 內翻案，過期自動確認。）
```

0 筆時輸出：`昨日無拍板。`（不省略，確認系統正常）

### Step 5：更新 memory/journal.md

追加一行日誌：
```
- {YYYY-MM-DD} 09:00 日報：昨日 {N} 筆拍板，{M} 筆待決 L3，翻案率 ceo {%} / cto {%}
```

## 翻案按鈕行為

按下 `[翻案]` 後：
1. 系統要求輸入翻案原因（必填，空白拒絕）
2. 輸入後呼叫 `DecisionStore.overturn(decision_id, reason)`
3. 通知原決策者與 requester 回滾指示
4. 翻案原因寫入決策者 knowledge + BRAIN.md（呼叫 `write_knowledge_feedback`）

## 注意事項

- 此 Skill 由排程喚醒，**不監聽**即時訊息
- 日報必定送出，即使 0 筆也要發「昨日無拍板」
- 翻案操作走 Telegram InlineKeyboard callback（`overturn:{decision_id}` 格式）

---
author: paddyyang
name: ark-policy-translate
description: |
  將 Paddy 的方針語句（「以後 X 一律 Y」「規定 X」「把 X 的權限給 CTO」）
  轉為結構化方針 YAML，同步寫入相關 agent 的 BRAIN.md ARK:AGENT-NOTES
  與 Wiki decisions/policies/ 知識庫。
  使用此 Skill 當意圖分類判斷為 policy_update 時自動觸發。
---

# ark-policy-translate

將 Paddy 的口語方針轉為結構化記錄，讓 agent 可 recall 並遵守。

## 觸發條件

- 意圖分類判斷為 `policy_update`
- 訊息中有方針語句：「以後」「一律」「規定」「不准」「把.*權限」「下次遇到」

## 執行步驟

### Step 1：解析方針語句

從訊息提取以下欄位：

```yaml
scope: product | tech | authority-matrix | general
       # product → 影響 ceo-agent
       # tech    → 影響 cto-agent
       # authority-matrix → 需要更新 config/authority-matrix.yml
       # general → 影響全體 agent（AGENTS.md）
rule: {一句話方針，清楚說明規則}
effective_from: {今天日期 YYYY-MM-DD}
requires_matrix_update: true | false  # scope=authority-matrix 時設 true
```

### Step 2：判斷影響範圍並確認

若 `requires_matrix_update: true`（涉及 authority-matrix 結構性變更）：
- 先回覆 Paddy 草案內容，請求確認
- 格式：`✅ 已記錄方針草案，待你確認後更新矩陣`
- 等 Paddy 確認後才執行 Step 3-4

其他 scope：直接執行 Step 3-4，不需確認。

### Step 3：寫入 BRAIN.md ARK:AGENT-NOTES

依 scope 決定目標 agent：

| scope | 目標路徑 |
|-------|---------|
| product | `agents/ceo-agent/.kiro/steering/BRAIN.md` |
| tech | `agents/cto-agent/.kiro/steering/BRAIN.md` |
| general | `agents/*/`（全體 worker 的 BRAIN.md，若存在）|
| authority-matrix | `agents/ceo-agent/.kiro/steering/BRAIN.md` + `agents/cto-agent/.kiro/steering/BRAIN.md` |

在目標檔案的 `ARK:AGENT-NOTES` 段落追加：
```
- {YYYY-MM-DD} 方針：{rule}（Paddy 指示）
```

若段落不存在，在檔案末尾新建：
```markdown
## ARK:AGENT-NOTES

- {YYYY-MM-DD} 方針：{rule}（Paddy 指示）
```

### Step 4：寫入 Wiki decisions/policies/

路徑：`knowledge/wiki/decisions/policies/{YYYY-MM-DD}-{slug}.md`

格式：
```markdown
---
title: "{rule 前 20 字}"
type: concept
tags: [policy, {scope}]
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
status: mature
---

# 方針：{rule}

- **生效日期**：{effective_from}
- **範圍**：{scope}
- **規則**：{rule}
- **來源**：Paddy 口語指示（由 ark-agent 轉譯）
```

若 `knowledge/wiki/decisions/policies/` 目錄不存在，自動建立。

### Step 5：回覆 Paddy

```
✅ 已記錄方針：{rule 前 30 字}
影響範圍：{scope} agent
已更新：{目標 BRAIN.md 路徑}、{Wiki 路徑}
```

若 `requires_matrix_update: true`：
```
✅ 已記錄方針草案，待你確認後更新矩陣
草案：{rule}
確認後我會將 authority-matrix.yml version +1
```

## 範例

### 輸入：scope=product
```
Paddy：「以後 scope 一律從嚴，不隨意加功能到 MVP」
```
解析：
```yaml
scope: product
rule: MVP scope 一律從嚴，不得隨意加功能到 MVP
effective_from: 2026-07-30
requires_matrix_update: false
```
寫入 `agents/ceo-agent/.kiro/steering/BRAIN.md` 的 `ARK:AGENT-NOTES`。
寫入 `knowledge/wiki/decisions/policies/2026-07-30-mvp-scope-strict.md`。
回覆：`✅ 已記錄方針：MVP scope 從嚴，已更新 ceo-agent 記憶與 Wiki`

### 輸入：scope=authority-matrix
```
Paddy：「把採購決定的權限給 CTO，$100 以內的自己決」
```
解析：
```yaml
scope: authority-matrix
rule: 採購 $100 以內 → cto-agent L2 自決（原為 L3）
effective_from: 2026-07-30
requires_matrix_update: true
```
回覆：`✅ 已記錄方針草案，待你確認後更新矩陣`

Paddy 確認後：
- 更新 `config/authority-matrix.yml`：L3 triggers 移除「$100 以內採購」，加入 tech L2 examples
- version +1
- 回覆：`✅ authority-matrix.yml 已更新至 v{N+1}`

## 注意事項

- scope 判斷不確定時，詢問 Paddy：「這個方針主要影響哪個 domain？（product/tech/全體）」
- 方針語句不等於任務請求，不觸發 route_* 意圖
- `requires_matrix_update: true` 的草案，24h 內未確認 → 自動丟棄，不執行
- 已有相同 slug 的 Wiki 頁面 → 更新 updated 欄位並 append 新規則

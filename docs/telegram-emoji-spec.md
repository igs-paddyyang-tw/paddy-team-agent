# Telegram 回饋圖示規範

> Bot 所有回應使用的 emoji 語意對照表。

## 狀態圖示

| 圖示 | 語意 | 出現位置 |
|------|------|---------|
| 🟢 | idle / available / 成功 | /agents /status /runtimes |
| 🔵 | busy / executing / 進行中 | /agents /board /status |
| 🟡 | claimed / pending / 等待 | /board |
| 🔴 | offline / failed / blocked / unavailable | /agents /runtimes /board |
| ⚪ | unknown | fallback |

## 結果圖示

| 圖示 | 場景 | 範例 |
|------|------|------|
| ✅ | 成功完成 | `✅ <b>任務完成</b>` |
| ❌ | 失敗/取消 | `❌ <b>任務失敗</b>` |
| ⚠️ | 警告 | `⚠️ <b>預算警報</b>` |
| 🚫 | Blocker | `🚫 <b>Blocker 回報</b>` |
| 🔄 | 重試/重啟 | `🔄 任務已重新排入佇列` |
| ⏳ | 處理中（會被覆蓋） | `⏳ <b>agent</b> 處理中...` |

## 功能圖示

| 圖示 | 用途 |
|------|------|
| 📋 | 任務/看板/佇列 |
| 📊 | 統計數據 |
| 💰 | 費用 |
| 🤖 | Agent |
| 🖥️ | Runtime |
| ⏱️ | 耗時 |
| 📝 | 輸出摘要 |
| 🧠 | Leader |
| ⚙️ | Admin |
| 💻 | Worker/Coder |
| 🧪 | QA |

## 角色圖示

| 圖示 | 角色 |
|------|------|
| ⚙️ | admin |
| 🧠 | leader |
| 💻 | worker (default) |
| 🤖 | ai-dev |
| 🧪 | qa |

## 優先級圖示

| 圖示 | 優先級 |
|------|--------|
| 🔴 | 1 (urgent) |
| 🟠 | 2 (high) |
| 🔵 | 3 (normal) |
| ⚪ | 4 (low) |

## 卡片模板

### 任務完成

```
✅ <b>任務完成</b>

📋 #t-abc — Build REST API
🤖 coder-agent
⏱️ 耗時: 45 秒
💰 消耗: $0.0150
```

### 任務失敗

```
❌ <b>任務失敗</b>

📋 #t-abc
原因: timeout after 120s
```

### Blocker

```
🚫 <b>Blocker 回報</b>

🤖 admin-agent 執行 #t-jkl 時遇到阻塞：

「需要 DB 權限才能執行 migration」
```

### 預算警報

```
⚠️ <b>預算警報</b>

今日費用已達 80%
$24.00 / $30.00
```

### Agent 重啟

```
🔄 <b>自動重啟</b>

Agent: coder-agent
離線: 310s
重啟次數: #2
```

## 設計原則

- 顏色語意一致（🟢成功 🔵進行 🟡等待 🔴失敗）
- 結論先行（第一行就是結果）
- HTML `<b>` 粗體標題
- 輸出截斷 200 字 + `...`
- `⏳ 處理中` 完成後用 `edit_message_text` 覆蓋

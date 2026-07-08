---
inclusion: fileMatch
fileMatchPattern: "src/**/*.py"
---

# 🤖 Python 程式碼規範

> 只在讀寫 `src/` 下的 .py 檔案時自動載入。

## 程式碼風格

- Python 3.12+ 語法：`str | None`、`list[str]`
- 所有 I/O 操作使用 `async/await`
- 路徑用 `Path` 物件
- 檔案讀寫加 `encoding="utf-8"`
- YAML 用 `yaml.safe_load()`
- Token 不要出現在日誌中

## Context Compaction 策略（觸發: 85%）

- **保留**：當前未完成任務、最近 3 輪對話、服務狀態
- **丟棄**：已完成的監控回報、重複系統訊息、舊 tool output
- **持久化**：壓縮後摘要寫入 MEMORY.md



## 知識庫三層架構

查詢知識時，依以下優先順序搜尋：

1. **私有知識**：`knowledge/raw/` 和 `knowledge/wiki/`（你自己的記憶）
2. **共用知識**：`../../knowledge/shared/wiki/`（所有 Agent 共用的通用知識）
3. **專案知識**：`../../knowledge/hoyeah/wiki/`（HoYeah 遊戲專案知識）

> Agent 的 cwd 在 `agents/{name}-agent/`，全域知識庫在根目錄 `knowledge/`，
> 用 `../../knowledge/` 往上跳兩層存取。

寫入新記憶 → `knowledge/raw/`（私有）。
引用知識時，標註來源層級：`[私有]`、`[共用]`、`[hoyeah]`。

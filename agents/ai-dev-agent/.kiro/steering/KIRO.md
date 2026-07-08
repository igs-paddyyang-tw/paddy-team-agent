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

## Context Compaction 策略（觸發: 75%）

- **保留**：當前未完成任務上下文、最近 5 輪對話、Prompt 設計決策
- **丟棄**：已完成任務詳細對話、重複系統訊息、舊 tool output
- **持久化**：壓縮後摘要寫入 MEMORY.md


## 知識庫存取

查詢知識時，依以下優先順序搜尋：

1. **私有知識**：`knowledge/raw/` 和 `knowledge/wiki/`（你自己的記憶）
2. **共用知識**：`knowledge/shared/wiki/`（所有 Agent 共用的通用知識）
3. **專案知識**：`knowledge/hoyeah/wiki/`（HoYeah 遊戲專案知識）

寫入新記憶時，寫到 `knowledge/raw/`（私有）。
引用知識時，標註來源層級：`[私有]`、`[共用]`、`[hoyeah]`。

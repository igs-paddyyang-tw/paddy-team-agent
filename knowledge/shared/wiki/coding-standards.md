---
title: "全團隊程式碼規範"
type: system
tags: [coding, standards, python, typescript]
created: 2026-07-08
updated: 2026-07-08
status: mature
---

# 全團隊程式碼規範

## Python

| 項目 | 規則 |
|------|------|
| 版本 | 3.12+ |
| 型別標註 | `str | None`、`list[str]`（不用 Optional/List） |
| async | 所有 I/O 用 `async/await` |
| 路徑 | 用 `Path` 物件 |
| 編碼 | 檔案讀寫加 `encoding="utf-8"` |
| YAML | 用 `yaml.safe_load()` |
| 日誌 | `log = logging.getLogger(__name__)` + `%s` 格式 |
| docstring | 模組第一行 `"""一句話說明。"""` |
| import | `from __future__ import annotations` 放第二行 |

## 檔案結構

```python
"""模組一句話說明。"""
from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)
```

## 命名規則

| 對象 | 格式 | 範例 |
|------|------|------|
| 檔案 | snake_case | `wiki_engine.py` |
| 類別 | PascalCase | `WikiEngine` |
| 函式 | snake_case | `rebuild_index()` |
| 常數 | UPPER_SNAKE | `MAX_RETRIES` |
| 私有 | 前綴底線 | `_parse_frontmatter()` |

## 禁止事項

- ❌ 不用 `print()`，用 `log.info()`
- ❌ 不用 f-string 在 log 裡（`log.info("x=%s", x)`）
- ❌ Token/Secret 不出現在日誌或程式碼中
- ❌ 不用 `import *`
- ❌ 不在 async 函式裡呼叫阻塞 I/O

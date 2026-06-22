---
title: "Telegram Bot 即時回饋互動"
type: onepager
status: implemented
created: 2026-06-17
updated: 2026-06-17
language: zh-TW
author: admin-agent
ref: docs/reqs/qa-instant-feedback-req.md
---

# Telegram Bot 即時回饋互動

## 實作摘要

P1 已實作於 `src/tg_ui/handlers/messages.py`：

1. **Reaction 狀態機**：👀（收到）→ ✅（完成）/ ❌（失敗）
2. **Chat Action Timer**：每 4 秒 `typing`，處理完畢自動停止
3. **整合至 handle_message**：不產生中間訊息

## 驗收對照

| # | 條件 | 狀態 |
|---|------|------|
| AC-1 | 收到訊息後 < 1 秒出現 👀 | ✅ |
| AC-2 | 處理時間 > 5 秒時 typing 狀態不斷線 | ✅ |
| AC-3 | 回覆後 👀 → ✅ 無殘留 | ✅ |
| AC-4 | 例外時 ❌ + 錯誤摘要（不暴露 stack trace） | ✅ |
| AC-5 | 對話中不產生「收到」「正在處理」等中間訊息 | ✅ |

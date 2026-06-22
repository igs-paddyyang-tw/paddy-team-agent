---
title: "ai-dev-agent Knowledge Schema"
type: system
created: 2026-06-17
updated: 2026-06-17
---

# Wiki Schema v3.0

## 目錄結構

```
knowledge/
├── raw/          → 唯讀原始資料
├── wiki/         → 結構化知識頁面
├── schema.md     → 本文件
├── index.md      → 索引目錄
└── log.md        → 操作日誌（append-only）
```

## 操作規則

| 規則 | 說明 |
|------|------|
| raw/ 唯讀 | LLM 只讀不改 |
| 修改後同步 | 改 wiki → 必須更新 index.md + log.md |
| log append-only | 禁止刪除舊記錄 |

## 適合存放的知識

- LLM API 踩坑（rate limit、token 計算、模型差異）
- Prompt pattern（CoT、few-shot、structured output）
- RAG 策略（chunk size、embedding、retrieval）
- MCP 開發紀錄（Tool 設計、Protocol 整合）
- Agent 系統設計（multi-agent、state machine）

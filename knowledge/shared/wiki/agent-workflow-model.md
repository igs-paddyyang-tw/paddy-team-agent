---
title: "Agent 運作流程模型"
type: concept
tags: [agent, workflow, architecture, LLM, MCP]
sources: [raw/agent-workflow-reference.md]
related: [platform-architecture, agent-collaboration]
created: 2026-06-27
updated: 2026-06-27
status: developing
---

# Agent 運作流程模型

## 摘要

描述通用 AI Agent 的完整運作流程，從使用者輸入到最終回覆的 7 個階段。此為參考模型，用於對照 AI Team Agent 平台的實際架構差異。

## 7 階段流程

| # | 階段 | 職責 | 關鍵動作 |
|---|------|------|----------|
| 1 | 輸入解析 | NLU | 意圖識別、實體提取、參數解析 |
| 2 | 系統提詞 | Prompt | 定義角色、能力、規範 |
| 3 | LLM 規劃 | Planning | 理解意圖 → 規劃步驟 → 識別工具 → 制定策略 |
| 4 | 工具執行 | Execution | Skills + MCP + 知識庫查詢 |
| 5 | 迭代驗證 | Validation | 每次工具調用後驗證輸出、決定下一步 |
| 6 | 結果整合 | Synthesis | 合併去重 → 格式化 → 添加元數據 |
| 7 | 記憶更新 | Memory | 記錄執行過程、更新會話歷史、優化檢索 |

## 工具執行層三元件

1. **Skills（技能層）** — 預定義的能力模組（數據分析、文件轉換、郵件發送等）
2. **MCP 伺服器** — 外部服務整合（Google Drive、Gmail、Asana 等）
3. **知識庫** — 內部文件查詢（政策、範本、流程文件）

## 與 AI Team Agent 架構對照

| 參考模型 | AI Team Agent 對應 | 狀態 |
|---------|-------------------|------|
| 單 Agent 全自動 | 多 Agent 協作（PM 分派 Worker） | ✅ 更進階 |
| NLU 意圖解析 | LLM 隱式理解 + handlers 路由 | ✅ 等效 |
| Step-by-step 規劃 | ark-project-planning SDD 流程 | ✅ 更結構化 |
| Skills 執行 | 55 個 ark-* Skills | ✅ 豐富 |
| MCP 外部整合 | MCP Registry 存在但 connector 少 | ⚠️ 待擴充 |
| 迭代驗證 | Output Marker + progress_parser | ✅ 有對應 |
| 知識庫更新 | wiki_engine 規劃但內容空 | ⚠️ 待充實 |
| 執行時間回報 | audit_logger 記錄但不回傳使用者 | ⚠️ 可改善 |
| 前提條件檢查 | 無 pre-flight check 機制 | ❌ 缺少 |

## 範例情境摘要

**任務**：分析上月客戶反饋 → 生成改進方案 → 發送給產品經理

**流程**：
1. NLU 拆出 3 個意圖（分析/生成/發送）+ 3 個實體
2. 識別 3 個 Skills + 4 份知識文件 + 2 個 MCP
3. 4 階段執行：數據蒐集 → 數據處理 → 報告生成 → 發送記錄
4. 每階段有前提條件檢查 + 輸出驗證
5. 最終回傳結構化摘要（含性能指標）

## 改善建議（針對 AI Team Agent）

1. **補充 MCP connector** — 優先：Google Drive、Gmail、Slack
2. **建立 pre-flight check** — 任務開始前驗證資源/權限可用
3. **執行時間回報** — reply 中加入 ⏱️ 耗時統計
4. **知識庫自動累積** — 每次任務完成後自動 ingest 到 wiki
5. **輕量任務快速通道** — 簡單任務不需要走完整 SDD 流程

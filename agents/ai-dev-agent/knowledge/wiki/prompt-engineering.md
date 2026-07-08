---
title: "Prompt 工程最佳實踐"
type: guide
tags: [prompt, llm, few-shot, cot, system-prompt]
created: 2026-07-08
updated: 2026-07-08
status: evergreen
---

# Prompt 工程最佳實踐

## System Prompt 結構

一個有效的 System Prompt 應包含以下層次：

1. **Identity（身份）** — 定義角色、專長、語氣
2. **Capabilities（能力）** — 列出可使用的工具和技能
3. **Rules（約束）** — 設定邊界、安全規範、輸出格式
4. **Context（上下文）** — 提供任務背景和領域知識
5. **Examples（範例）** — 具體的輸入/輸出範例

結構化建議：使用 XML 標籤（`<identity>`, `<rules>`）分段，方便模型解析。

## Few-shot Prompting

- **何時使用**：輸出格式固定、分類任務、風格遷移
- **最佳數量**：3-5 個範例覆蓋邊界情況
- **排列順序**：將最相關的範例放在最後（recency bias）
- **負面範例**：加入 1-2 個「不要這樣做」的反例提升準確率

## Chain-of-Thought (CoT)

| 策略 | 適用場景 | 範例觸發詞 |
|------|----------|------------|
| Zero-shot CoT | 通用推理 | "Let's think step by step" |
| Manual CoT | 複雜多步推理 | 手寫推理步驟作為範例 |
| Self-Consistency | 需要高準確率 | 多次採樣取多數票 |
| Tree-of-Thought | 探索性問題 | 分支推理 + 回溯 |

**注意**：CoT 在簡單任務上可能降低效率，僅在推理密集任務使用。

## Temperature 選擇指南

| Temperature | 用途 | 範例 |
|-------------|------|------|
| 0.0 - 0.2 | 確定性輸出、程式碼生成、JSON 格式化 | API 回應、SQL 生成 |
| 0.3 - 0.5 | 平衡創意與準確 | 技術文件撰寫、摘要 |
| 0.6 - 0.8 | 創意寫作、腦力激盪 | 行銷文案、故事生成 |
| 0.9 - 1.0 | 高度創意、多樣化輸出 | 詩歌、角色扮演 |

## 實戰技巧

- **Prompt 版本管理**：將 prompt 視為程式碼，用 Git 管理迭代
- **A/B 測試**：使用 eval dataset 量化 prompt 改進效果
- **Token 預算**：先估算 input + output tokens，避免截斷
- **格式指令**：明確指定輸出格式（JSON Schema, Markdown, CSV）
- **防護欄**：加入 "If unsure, say I don't know" 降低幻覺率

---
title: "AI Team Agent 架構技術文件 — GitHub Pages 發佈"
type: onepager
status: draft
created: 2026-06-24
updated: 2026-06-24
language: zh-TW
author: pm-agent
---

# AI Team Agent 架構技術文件 — GitHub Pages 發佈

## 問題陳述

目前專案架構知識散落在程式碼、MEMORY.md、各 Agent 的 steering 文件中，缺乏一份可視覺化瀏覽的技術總覽文件。需要產出結構化 Markdown 架構文件並轉為 HTML，在 GitHub Pages 上以 `ai-team-agent.html` 開啟即可瀏覽。

## 目標

1. 產出一份完整的 `docs/architecture.md` — 涵蓋系統總覽、模組分層、資料流、團隊組成
2. 將 Markdown 轉為獨立 HTML 檔案 `ai-team-agent.html`，放在 repo 根目錄
3. 啟用 GitHub Pages，使用者可直接瀏覽 `https://{user}.github.io/{repo}/ai-team-agent.html`

## 非目標

- 不建立完整靜態站點框架（Jekyll / Hugo）
- 不需要 CI/CD 自動重建（手動更新即可）
- 不含 API 參考文件（僅架構層級）

## 方案

### 產出物

| 檔案 | 用途 |
|------|------|
| `docs/architecture.md` | 原始 Markdown 架構文件（維護用） |
| `ai-team-agent.html` | 獨立 HTML（GitHub Pages 展示用） |

### architecture.md 內容結構

```
1. 系統總覽（一段話 + 元件圖）
2. 技術棧
3. 目錄結構
4. 核心模組
   - src/runtime（進程管理、排程）
   - src/coordinator（DB、EventBus、A2A）
   - src/gateway（API、Telegram）
   - src/business（業務邏輯）
5. Agent 團隊
6. Skills 概覽（55 個分類）
7. 資料流（使用者訊息 → 回覆路徑）
8. 部署架構（Docker Compose）
9. 設定檔說明
```

### HTML 轉換方式

使用 Python `markdown` 套件（已安裝於 .venv）產生 HTML body，包裹在一個含有樣式的 standalone HTML 模板中：

```bash
python scripts/build_architecture_html.py
```

### GitHub Pages 設定

- **Source**: Deploy from branch → `main` → `/ (root)`
- 瀏覽路徑：`https://{user}.github.io/kiro-cli/ai-team-agent.html`
- 或在 repo 根目錄直接開啟 `ai-team-agent.html`

## 執行計畫

| # | 任務 | 負責 | 大小 | 驗收 |
|---|------|------|------|------|
| 1 | 撰寫 `docs/architecture.md` | pm-agent | M | 含 9 個章節，Mermaid 圖表 |
| 2 | 建立 `scripts/build_architecture_html.py` | coder-agent | S | 執行後產出 `ai-team-agent.html` |
| 3 | 產出 `ai-team-agent.html` 到根目錄 | coder-agent | XS | 可在瀏覽器直接開啟 |
| 4 | GitHub Pages 設定說明 | pm-agent | XS | README 補充說明 |

## 風險

| 風險 | 緩解 |
|------|------|
| Mermaid 圖表在靜態 HTML 不渲染 | 嵌入 mermaid.js CDN |
| 文件很快過時 | 加入「最後更新」時間戳 + 建議定期重建 |

## 成功指標

- [ ] `ai-team-agent.html` 在瀏覽器開啟可見完整架構文件
- [ ] 含 Mermaid 圖表正常渲染
- [ ] GitHub Pages 可正常存取

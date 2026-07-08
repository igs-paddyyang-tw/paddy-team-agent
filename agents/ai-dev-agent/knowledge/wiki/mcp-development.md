---
title: "MCP 開發指南"
type: guide
tags: [mcp, server, tool, transport, protocol]
created: 2026-07-08
updated: 2026-07-08
status: evergreen
---

# MCP 開發指南

## Model Context Protocol 概述

MCP 是連接 AI 模型與外部工具/資料的標準化協議，定義了 Client-Server 架構：
- **Host**：AI 應用（如 Kiro CLI、Claude Desktop）
- **Client**：協議層，管理與 Server 的連線
- **Server**：提供 Tools、Resources、Prompts 給 Client 使用

## Server 結構

```
my-mcp-server/
├── package.json          # 依賴和啟動腳本
├── src/
│   ├── index.ts          # 入口：建立 Server 實例
│   ├── tools/            # Tool 定義（一個檔案一個 Tool）
│   │   ├── search.ts
│   │   └── execute.ts
│   ├── resources/        # Resource Provider
│   └── prompts/          # Prompt Template
├── tests/
│   └── tools.test.ts
└── tsconfig.json
```

**入口模板（TypeScript）**：
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const server = new McpServer({ name: "my-server", version: "1.0.0" });
server.tool("search", schema, handler);
server.start(transport);
```

## Tool 定義

每個 Tool 需包含：
- **name**：唯一識別名稱（kebab-case）
- **description**：清楚描述功能、使用時機
- **inputSchema**：JSON Schema 定義參數（必填/選填/型別）
- **handler**：實際執行邏輯，回傳 `{ content: [...] }`

**設計原則**：
- 一個 Tool 做一件事（Single Responsibility）
- Description 寫給 LLM 看：說明「何時」和「為何」使用
- 回傳結構化 content（text, image, resource）
- 錯誤時回傳 `{ isError: true, content: [...] }`

## Transport 模式

| 模式 | 使用場景 | 特色 |
|------|----------|------|
| stdio | 本地開發、CLI 整合 | 最簡單，process stdin/stdout |
| SSE (HTTP) | 遠端部署、多 Client | Server-Sent Events，支援認證 |
| Streamable HTTP | 生產環境 | 雙向串流，支援斷線重連 |

**本地開發推薦 stdio**：
```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": { "API_KEY": "${API_KEY}" }
    }
  }
}
```

## 測試方法

1. **單元測試**：直接呼叫 handler function，驗證回傳格式
2. **整合測試**：使用 MCP Inspector 互動式測試 Tool
3. **E2E 測試**：透過 Client SDK 模擬完整呼叫流程
4. **錯誤案例**：測試缺少參數、無效輸入、超時情況

```bash
# MCP Inspector — 互動式除錯
npx @modelcontextprotocol/inspector node dist/index.js

# 手動 stdio 測試
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node dist/index.js
```

## 實戰經驗

- **環境變數**：敏感資訊（Token、Key）一律用 env 注入，不寫死
- **Rate Limiting**：外部 API 呼叫加入 retry + backoff
- **Logging**：用 stderr 輸出 debug log（stdout 保留給 MCP 協議）
- **版本管理**：語意化版本，breaking change 時升 major
- **autoApprove**：僅允許唯讀操作自動批准，寫入操作需確認

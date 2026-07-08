---
title: "RAG 架構模式"
type: guide
tags: [rag, embedding, vector-db, chunking, retrieval]
created: 2026-07-08
updated: 2026-07-08
status: evergreen
---

# RAG 架構模式

## 整體流程

```
Documents → Ingest → Chunk → Embed → Vector Store
                                          ↓
User Query → Embed Query → Retrieve Top-K → Rerank → Generate Answer
```

## Ingest 流程

1. **文件載入**：支援 PDF, Markdown, HTML, Code, CSV 等格式
2. **前處理**：清理 HTML 標籤、去除重複、正規化文字
3. **元數據提取**：標題、作者、日期、標籤、路徑
4. **增量更新**：比對 mtime/hash 僅處理變更檔案
5. **Pipeline 設計**：使用 DAG 編排，支援並行處理

## Chunking 策略

| 策略 | 適用場景 | 優缺點 |
|------|----------|--------|
| Fixed-size (512 tokens) | 通用場景 | 簡單但可能切斷語意 |
| Recursive split | 結構化文件 | 依分隔符遞迴切分，保留結構 |
| Semantic chunking | 長文、論文 | 依語意邊界切分，品質最高 |
| Sentence window | 對話、FAQ | 以句子為單位 + 前後文窗口 |
| Parent-child | 階層文件 | 檢索 child，回傳 parent 上下文 |

**經驗法則**：
- Chunk size 256-1024 tokens，overlap 10-20%
- 加入 chunk metadata（source, section, page）提升過濾能力

## Embedding 選型

| 模型 | 維度 | 適用場景 | 特色 |
|------|------|----------|------|
| text-embedding-3-small | 1536 | 通用、成本敏感 | OpenAI，性價比高 |
| text-embedding-3-large | 3072 | 高精度需求 | OpenAI，最佳品質 |
| Cohere embed-v3 | 1024 | 多語言場景 | 支援 100+ 語言 |
| BGE-M3 | 1024 | 自建部署 | 開源，多語言 |
| Amazon Titan Embeddings | 1024/1536 | AWS 生態系 | Bedrock 原生整合 |

## Retrieval 策略

- **Hybrid Search**：結合 BM25（關鍵字）+ Vector（語意）提升召回率
- **Reranking**：使用 Cross-encoder 重排 Top-K 結果
- **Query Expansion**：HyDE（生成假設答案再檢索）提升相關性
- **Metadata Filter**：先過濾分類/日期再做向量搜索，降低噪音
- **Multi-Query**：將用戶問題改寫為多個角度再合併結果

## Generation 最佳實踐

- 將 retrieved context 放在 prompt 中間（避免 lost-in-the-middle）
- 加入 citation 指令：要求模型標註來源 chunk
- 設定 confidence threshold：相似度低於閾值時回答 "不確定"
- 使用 streaming 降低用戶感知延遲
- 監控 faithfulness（答案是否基於 context）避免幻覺

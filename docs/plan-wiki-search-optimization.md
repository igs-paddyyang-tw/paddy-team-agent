---
title: "ark-wiki-engine 搜尋優化執行計劃"
type: plan
status: approved
created: 2026-07-08
---

# ark-wiki-engine 搜尋優化執行計劃

## 目標

把 WikiQuery 從「能跑但不好用」升級為「四層金字塔搜尋管線」，保證查詢永不掛零。

```
Layer 3: Rerank（選配，有 LLM 時用）
Layer 2: 三路混合（BM25 + 語意向量 + 圖譜擴散）→ RRF 融合
Layer 1: BM25 持久化索引（jieba + bigram 保險絲）
Layer 0: 保底層（metadata 精確查找 + 子字串掃描，永不掛零）
```

---

## Phase 0：保底層 + Metadata（~1.5hr）

### 0-1：建立 .index/ 目錄結構

```
knowledge/.index/
├── metadata.json      ← 所有頁面的 slug/title/aliases/tags 快速查表
├── userdict.txt       ← jieba 自定義詞典（從 aliases + title 自動產生）
├── manifest.json      ← 索引版本 + 最後重建時間 + 頁面數
└── bm25s/             ← Phase 1 用（bm25s 持久化索引）
```

### 0-2：metadata.json 格式

```json
[
  {
    "slug": "ocean-king-analysis",
    "title": "Ocean King 捕魚機系列競品分析",
    "aliases": ["Ocean King", "捕魚機", "海洋王"],
    "tags": ["遊戲", "競品", "捕魚"],
    "path": "wiki/ocean-king-analysis.md",
    "updated": "2026-07-08"
  }
]
```

### 0-3：查詢流程（Layer 0 保底）

```python
def query_layer0(q: str, metadata: list[dict]) -> list[str]:
    """保底層：精確匹配 + 子字串掃描。永遠有結果。"""
    # 1. 精確匹配：slug / title / aliases 命中 → 直接回該頁面
    for entry in metadata:
        if q.lower() in [entry["slug"], entry["title"].lower()] + [a.lower() for a in entry.get("aliases", [])]:
            return [entry["path"]]

    # 2. 子字串掃描：mmap + casefold 逐檔掃（數百頁 <100ms）
    hits = []
    for entry in metadata:
        content = read_body(entry["path"])  # 跳過 frontmatter
        if q.lower() in content.lower():
            hits.append(entry["path"])
    return hits
```

> 設計決策：不用 SQLite，直接 JSON `json.load` 秒讀，全記憶體查找 <1ms。數百頁規模 SQLite 是 overkill。

### 0-4：新增檔案

| 檔案 | 用途 |
|------|------|
| `src/wiki/indexer.py` | 索引建置器（metadata + userdict + manifest） |

---

## Phase 1：BM25 持久化索引（~2hr）

### 1-1：分詞策略

```python
import jieba

def tokenize(text: str) -> list[str]:
    """jieba cut_for_search + bigram 保險絲。"""
    # 載入自定義詞典（aliases + title 自動產生）
    jieba.load_userdict("knowledge/.index/userdict.txt")

    tokens = list(jieba.cut_for_search(text))

    # bigram 保險絲：解決未登錄詞
    bigrams = [text[i:i+2] for i in range(len(text) - 1) if not text[i].isspace()]
    tokens.extend(bigrams)

    # 過濾停用詞
    stopwords = {"的", "是", "了", "在", "有", "什麼", "嗎", "呢", "可以", "怎麼", "一個", "和", "與"}
    return [t for t in tokens if t.strip() and t not in stopwords]
```

### 1-2：bm25s 持久化索引

```python
import bm25s

def build_bm25_index(pages: list[dict]) -> None:
    """建置 BM25 索引並持久化到 .index/bm25s/。"""
    corpus = []
    for page in pages:
        body = read_body(page["path"])
        tokens = tokenize(body)
        corpus.append(tokens)

    retriever = bm25s.BM25()
    retriever.index(corpus)
    retriever.save("knowledge/.index/bm25s")


def query_bm25(q: str, top_k: int = 5) -> list[tuple[str, float]]:
    """BM25 查詢。"""
    retriever = bm25s.BM25.load("knowledge/.index/bm25s")
    tokens = tokenize(q)
    results, scores = retriever.retrieve([tokens], k=top_k)
    return [(results[0][i], scores[0][i]) for i in range(len(results[0]))]
```

### 1-3：欄位加權（title × 3, tags × 2, body × 1）

```python
def build_weighted_corpus(page: dict) -> str:
    """用文本重複實現欄位加權（bm25s 無 field boosting）。"""
    title = page["title"]
    tags = " ".join(page.get("tags", []))
    body = read_body(page["path"])

    # title 重複 3 次，tags 重複 2 次
    return f"{title} {title} {title} {tags} {tags} {body}"
```

### 1-4：新增依賴

```
bm25s>=0.2
jieba>=0.42
```

---

## Phase 2：三路混合搜尋（~2.5hr）

### 2-1：語意向量（選配，有 numpy 時啟用）

```python
# 建議用 BAAI/bge-m3（天然中英混合）
# 數百頁用 numpy cosine 暴力搜即可，不需向量 DB

import numpy as np

def cosine_search(query_vec: np.ndarray, corpus_vecs: np.ndarray, top_k: int = 5):
    """暴力 cosine similarity。數百頁完全 OK。"""
    scores = corpus_vecs @ query_vec / (
        np.linalg.norm(corpus_vecs, axis=1) * np.linalg.norm(query_vec)
    )
    top_idx = np.argsort(scores)[-top_k:][::-1]
    return [(idx, scores[idx]) for idx in top_idx]
```

### 2-2：圖譜擴散

```python
def graph_expand(seed_pages: list[str], depth: int = 1) -> list[str]:
    """從種子頁面沿 [[wikilink]] 和 related 擴散。"""
    expanded = set(seed_pages)
    for _ in range(depth):
        for page in list(expanded):
            links = extract_wikilinks(page)
            related = get_frontmatter(page).get("related", [])
            expanded.update(links + related)
    return list(expanded - set(seed_pages))
```

### 2-3：RRF 融合

```python
def rrf_fuse(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal Rank Fusion。"""
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked):
            scores[doc] = scores.get(doc, 0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

### 2-4：四層查詢管線整合

```python
async def query(q: str, top_k: int = 5) -> list[dict]:
    """四層金字塔查詢。"""
    # Layer 0: 保底（永不掛零）
    layer0_hits = query_layer0(q, metadata)
    if is_exact_match(layer0_hits):
        return format_results(layer0_hits)

    # Layer 1: BM25
    bm25_results = query_bm25(q, top_k=top_k * 2)

    # Layer 2: 三路混合
    semantic_results = cosine_search(embed(q), embeddings, top_k=top_k * 2) if has_embeddings else []
    graph_results = graph_expand([r[0] for r in bm25_results[:3]])

    # RRF 融合
    fused = rrf_fuse([
        [r[0] for r in bm25_results],
        [r[0] for r in semantic_results],
        graph_results,
    ])

    # 如果融合結果為空，Layer 0 兜底
    final = fused[:top_k] if fused else layer0_hits

    # 段落摘要擷取
    return format_results_with_summary(final, q)
```

---

## Phase 3：Rerank 選配（~30min）

```python
# 有 LLM API 時啟用，否則跳過
async def rerank(q: str, candidates: list[dict], top_k: int = 3) -> list[dict]:
    """LLM rerank — 讓 Gemini 從候選中挑最相關的。"""
    if not gemini_available():
        return candidates[:top_k]

    prompt = f"問題：{q}\n\n候選：\n"
    for i, c in enumerate(candidates):
        prompt += f"{i+1}. [{c['title']}] {c['summary'][:200]}\n"
    prompt += f"\n請回傳最相關的 {top_k} 個編號（用逗號分隔）："

    response = await gemini_chat(prompt)
    # 解析編號...
    return reranked
```

---

## Ingest 觸發索引重建

```python
def ingest():
    """匯入完成後自動觸發索引重建。"""
    # ... 現有 ingest 邏輯 ...

    # 觸發索引重建
    rebuild_index()


def rebuild_index():
    """重建所有搜尋索引。"""
    pages = scan_wiki_pages()

    # 1. metadata.json
    build_metadata(pages)

    # 2. userdict.txt（從 title + aliases 產生）
    build_userdict(pages)

    # 3. bm25s 索引
    build_bm25_index(pages)

    # 4. embeddings（選配）
    if embedding_model_available():
        build_embeddings(pages)

    # 5. manifest.json
    write_manifest(page_count=len(pages))
```

---

## SKILL.md 修改清單

| 段落 | 修改內容 |
|------|---------|
| WikiQuerySkill 功能描述 | 改為「metadata 精確查找 → BM25 持久化索引 → 子字串兜底 → 段落摘要 → 排序」 |
| WikiHybridSearchSkill 功能描述 | 改為「四層搜尋管線：metadata + bm25s + 語意向量 + 圖譜擴散 → RRF 融合（Layer 0 保底永不掛零）」 |
| WikiIngestSkill 功能描述 | 加入「→ 觸發索引重建（bm25s + metadata + userdict）」 |
| 產出檔案清單 | 新增 `wiki_indexer.py` |
| 目錄結構 | 新增 `.index/` 說明 |
| Frontmatter 欄位表 | 新增 `aliases` 欄位 |
| 注意事項 | 新增索引生命週期規則 |
| Query SOP | 更新為「metadata → BM25 → 兜底掃描」流程 |

---

## 產出檔案總覽

```
src/wiki/
├── engine.py              ← 修改：query() 改用四層管線
├── indexer.py             ← 🆕 索引建置器（metadata + bm25s + userdict + embeddings）
├── search/                ← 🆕 搜尋模組
│   ├── __init__.py
│   ├── layer0_exact.py    ← metadata 精確 + 子字串兜底
│   ├── layer1_bm25.py     ← bm25s 持久化索引 + jieba 分詞
│   ├── layer2_hybrid.py   ← 語意向量 + 圖譜擴散 + RRF 融合
│   └── layer3_rerank.py   ← LLM rerank（選配）
└── __init__.py

knowledge/
├── .index/                ← 🆕 持久化搜尋索引
│   ├── metadata.json
│   ├── userdict.txt
│   ├── manifest.json
│   └── bm25s/
├── raw/
├── wiki/
├── schema.md
├── index.md
└── log.md

templates/
└── wiki.html              ← 修改：搜尋結果顯示優化（高亮 + 段落摘要）

.gitignore                 ← 修改：加入 knowledge/.index/
```

---

## Web UI 更新

| 頁面 | 修改 |
|------|------|
| `wiki.html` | 搜尋結果改為段落摘要（非第一行），關鍵字高亮 |
| `api-docs.html` | 新增 `/api/v1/wiki/rebuild-index` 端點文件 |

---

## API 新增

```python
# 新增端點
POST /api/v1/wiki/rebuild-index    # 手動觸發索引重建
GET  /api/v1/wiki/index-status     # 查看索引狀態（manifest.json）
```

---

## 依賴更新（requirements.txt）

```
bm25s>=0.2
jieba>=0.42
numpy>=1.26           # 語意搜尋用（選配）
```

---

## 實作順序

| # | 任務 | 時間 | 依賴 |
|---|------|------|------|
| 1 | SKILL.md 更新（8 處修改） | 15 min | — |
| 2 | `.index/` 目錄 + metadata.json + manifest | 30 min | — |
| 3 | `indexer.py`（build_metadata + build_userdict） | 30 min | #2 |
| 4 | `layer0_exact.py`（精確 + 子字串兜底） | 30 min | #2 |
| 5 | `layer1_bm25.py`（jieba + bigram + bm25s） | 45 min | #3 |
| 6 | `engine.py` 重構 query() 走管線 | 30 min | #4 #5 |
| 7 | `layer2_hybrid.py`（語意 + 圖譜 + RRF） | 45 min | #5 |
| 8 | `layer3_rerank.py`（LLM 選配） | 20 min | #7 |
| 9 | Ingest 加觸發 rebuild_index | 15 min | #3 |
| 10 | API 新增 rebuild-index + index-status | 20 min | #3 |
| 11 | Web UI 搜尋結果優化 | 30 min | #6 |
| 12 | .gitignore + requirements.txt | 5 min | — |

**總計 ~5.5 小時**

---

## 驗收條件

- [ ] 查詢 aliases（如「Ocean King」）→ 精確命中，<10ms
- [ ] 查詢模糊關鍵字 → BM25 回傳相關頁面，有段落摘要
- [ ] 查詢完全不相關的詞 → Layer 0 子字串兜底，不掛零
- [ ] ingest 後自動重建索引（manifest.json 時間更新）
- [ ] .index/ 在 .gitignore 裡
- [ ] 無 bm25s / jieba 時 graceful fallback 到 Layer 0
- [ ] Web UI 搜尋結果顯示段落摘要 + 關鍵字高亮
- [ ] `/api/v1/wiki/rebuild-index` 能手動觸發

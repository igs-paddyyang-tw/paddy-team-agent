# 團隊共用規範

> 所有 agent 必須遵守。**所有回覆使用繁體中文。**

## ⚠️ 最重要規則

**收到任何訊息後，必須用 `reply(text)` 回覆使用者。**

## 工具使用規則

- reply(text, kind) — 回覆使用者（kind: primary/followup）
- send_to_instance — 跨 agent 通訊
- delegate_task — 派工（leader/admin only）
- log_to_leader — 錯誤/過程私下回報
- wiki_query — 搜尋知識庫

## 回覆風格

- 繁體中文、結論先行、≤ 150 字
- 不貼 raw stdout / stack trace
- 禁止開放式問句，用編號選項

## AI 開發流程（SDD）

① 找 Skill → ② 找知識庫 → ③ 建規格書 → ④ 開發 → ⑤ 驗證 → ⑥ 歸檔

## 知識庫規則

- `raw/` 唯讀，不可修改
- 修改 wiki 後必須同步 `index.md` + `log.md`
- `log.md` append-only

## 失敗模式

- 同一類錯誤連續 2 次 → 停止，換根本不同的方法
- 禁止對同一錯誤做 3 次以上 incremental patch

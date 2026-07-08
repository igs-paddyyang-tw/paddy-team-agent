---
name: ark-version-sync
description: |
  版本對齊 — 檢查 upstream 最新異動，比對本地差異，自動補上修改並產出 changelog。
  使用此 Skill 當使用者提及版本更新、對齊 upstream、同步最新版本、拉最新的改動、
  版本同步、upstream 差異、更新到最新、檢查上游更新、
  或任何需要將本地專案與 upstream 保持一致的場景。
metadata:
  author: paddyyang
  version: "1.0"
  updated: 2026-07-08
---

# ark-version-sync

版本對齊工具 — 自動檢查上游 (upstream) 最新改動，比對本地差異，補上修改並產出 changelog。

## 觸發條件

- 「幫我版本更新」、「對齊 upstream」
- 「同步最新版本」、「拉最新的改動」
- 「版本同步」、「upstream 差異」
- 「更新到最新」、「檢查上游更新」

---

## 上游來源

| 項目 | 值 |
|------|---|
| Repository | `igs-paddyyang-tw/ai-workshop` |
| Branch | `main` |
| Path | `samples/ai-team-agent` |
| URL | https://github.com/igs-paddyyang-tw/ai-workshop/tree/main/samples/ai-team-agent |

---

## 操作流程

### Phase 1：取得 upstream 變更清單

```bash
# 方法 A：使用 GitHub API（推薦）
# 取得 upstream 最近 commits
gh api repos/igs-paddyyang-tw/ai-workshop/commits \
  --jq '.[0:10] | .[] | {sha: .sha[:7], date: .commit.author.date[:10], message: .commit.message}' \
  -q 'path=samples/ai-team-agent'

# 方法 B：若本地有 clone
cd ~/kiro-cli/ai-workshop/samples/ai-team-agent
git log --oneline -10
```

### Phase 2：比對本地差異

```bash
# 列出 upstream 有但本地沒有的檔案
diff <(cd ~/kiro-cli/ai-workshop/samples/ai-team-agent && find . -name "*.py" -o -name "*.md" -o -name "*.yaml" -o -name "*.json" | sort) \
     <(cd ~/kiro-cli/ai-team-agent && find . -name "*.py" -o -name "*.md" -o -name "*.yaml" -o -name "*.json" | sort)

# 比對關鍵檔案內容差異
diff ~/kiro-cli/ai-workshop/samples/ai-team-agent/src/runtime/scheduler.py \
     ~/kiro-cli/ai-team-agent/src/runtime/scheduler.py
```

### Phase 3：智能分類差異

將差異分為以下類別：

| 類別 | 處理方式 |
|------|---------|
| 🆕 新增檔案 | 直接複製到本地 |
| 🔧 修改檔案（upstream 較新） | 比對後合併 |
| 🏠 本地專屬修改 | 保留不覆蓋（標記） |
| ⚠️ 衝突 | 列出讓使用者決定 |

判斷規則：
- `team.yaml`、`.env`、`agents/*/steering/MEMORY.md` → 本地專屬，不覆蓋
- `src/**/*.py`、`docs/**` → 以 upstream 為準，合併修改
- 新增的 Skill → 直接複製

### Phase 4：執行同步

```python
# 虛擬碼 — 實際由 admin-agent 執行
import shutil
from pathlib import Path

UPSTREAM = Path("~/kiro-cli/ai-workshop/samples/ai-team-agent")
LOCAL = Path("~/kiro-cli/ai-team-agent")

# 排除清單（本地專屬，不覆蓋）
EXCLUDE = {
    "team.yaml",
    ".env",
    "data/",
    "logs/",
    ".venv/",
    "agents/*/steering/MEMORY.md",
    "agents/*/knowledge/wiki/",
    "agents/*/output/",
}

for upstream_file in UPSTREAM.rglob("*"):
    rel = upstream_file.relative_to(UPSTREAM)
    if any(rel.match(pattern) for pattern in EXCLUDE):
        continue
    local_file = LOCAL / rel
    if not local_file.exists() or upstream_file.read_bytes() != local_file.read_bytes():
        # 複製或更新
        local_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(upstream_file, local_file)
```

### Phase 5：產出 Changelog

在 `docs/changelog-sync.md` 追加記錄：

```markdown
## [sync] YYYY-MM-DD HH:MM

**來源**: igs-paddyyang-tw/ai-workshop@{commit_sha[:7]}

### 🆕 新增
- `path/to/new-file.py` — 說明

### 🔧 修改
- `src/runtime/scheduler.py` — 修復 YAML key 不一致問題

### ⏭️ 跳過（本地專屬）
- `team.yaml` — 本地配置
- `agents/admin-agent/steering/MEMORY.md` — 本地記憶
```

---

## 輸出格式

```
📦 版本同步報告

🔄 Upstream: igs-paddyyang-tw/ai-workshop@abc1234
📅 同步時間: 2026-07-08 10:30

| 動作 | 檔案 | 說明 |
|------|------|------|
| 🆕 新增 | docs/agent-management-guide.md | Agent 管理手冊 |
| 🔧 更新 | src/runtime/scheduler.py | 修復 jobs key |
| ⏭️ 跳過 | team.yaml | 本地專屬配置 |
| ⚠️ 衝突 | — | 無 |

✅ 同步完成：新增 1 / 更新 1 / 跳過 1 / 衝突 0

[DONE] summary=版本同步完成，2 個檔案已更新
[ARTIFACT] path=docs/changelog-sync.md msg=同步記錄已追加
```

---

## 排除清單（不覆蓋）

以下路徑為本地專屬，同步時自動跳過：

```yaml
exclude:
  # 環境和配置
  - ".env"
  - "team.yaml"
  - "team-dev.yaml"
  - "team-ops.yaml"
  - "data/**"
  - "logs/**"
  - ".venv/**"
  - "__pycache__/**"
  
  # Agent 運行時資料
  - "agents/*/steering/MEMORY.md"
  - "agents/*/knowledge/wiki/**"
  - "agents/*/output/**"
  
  # 本地資料庫
  - "*.db"
  - "*.db-journal"
```

---

## 安全規則

1. **不刪除本地檔案** — 只新增和更新，不刪除
2. **衝突必須確認** — 雙方都有修改時，列出讓使用者決定
3. **備份修改檔** — 覆蓋前將本地版本備份到 `.sync-backup/`
4. **乾跑模式** — 預設先列出差異，使用者確認後才執行
5. **記錄追蹤** — 每次同步都追加到 changelog

---

## 互動流程

```
使用者: 幫我版本更新
  ↓
admin-agent:
  1. 檢查 upstream 最新 commit
  2. 比對本地差異
  3. 列出變更摘要（乾跑）
  4. 詢問：「以上 X 個檔案需要同步，要執行嗎？」
  ↓
使用者: 好 / 執行
  ↓
admin-agent:
  5. 執行同步
  6. 產出 changelog
  7. 回報結果

[DONE] summary=版本同步完成
```

---

## 注意事項

- 需要能存取 upstream repo（透過 GitHub API 或本地 clone）
- 本地 `~/kiro-cli/ai-workshop/` 是 upstream 的完整 clone
- 同步方向：upstream → 本地（單向）
- 大量檔案變更時分批處理，避免單次 commit 過大
- 建議同步後執行 `python start.py` 驗證啟動正常

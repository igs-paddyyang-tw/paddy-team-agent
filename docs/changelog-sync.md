# 📦 版本同步紀錄

> 每次執行 `ark-version-sync` 後自動追加記錄。
> 上游來源：https://github.com/igs-paddyyang-tw/ai-workshop/tree/main/samples/ai-team-agent

---

## [sync] 2026-07-08 10:30 — 初始對齊

**來源**: 本地手動修改（health_port 統一 + scheduler fix）

### 🔧 修改
- `src/runtime/scheduler.py` — 修復 YAML key 不一致（`schedules` → 支援 `jobs` fallback）
- `src/runtime/config.py` — health_port 預設值 13030 → 33333
- `team.yaml` / `team-dev.yaml` / `team-ops.yaml` — health_port: 33333
- `agents/*/mcp.json` (8 個) — port 13030 → 33333
- `.kiro/settings/mcp.json` — port 13030 → 33333
- `agents/admin-agent/.kiro/skills/ark-dashboard-health/SKILL.md` — port 更新

### 🆕 新增
- `docs/agent-management-guide.md` — Agent 新增/修改/移除操作手冊
- `agents/admin-agent/.kiro/skills/ark-version-sync/SKILL.md` — 版本同步 Skill
- `docs/changelog-sync.md` — 本檔案

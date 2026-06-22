"""validate_team.py — 驗證 ai-team-agent 結構完整性。"""
from pathlib import Path
import yaml
import sys

ROOT = Path(__file__).resolve().parent.parent
PASS = 0
FAIL = 0


def check(condition: bool, label: str):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")


def main():
    global PASS, FAIL
    print("🔍 驗證 ai-team-agent 結構完整性\n")

    # team.yaml
    print("── team.yaml ──")
    team_yaml = ROOT / "team.yaml"
    check(team_yaml.exists(), "team.yaml 存在")
    if team_yaml.exists():
        data = yaml.safe_load(team_yaml.read_text(encoding="utf-8"))
        check("defaults" in data, "有 defaults")
        check("cost_guard" in data, "有 cost_guard")
        check("hang_detector" in data, "有 hang_detector")
        check("health_port" in data, "有 health_port")
        instances = data.get("instances", {})
        check(len(instances) >= 2, f"≥ 2 instances ({len(instances)})")
        roles = [v.get("role") for v in instances.values()]
        check(roles.count("admin") == 1, "恰好 1 admin")
        check(roles.count("leader") == 1, "恰好 1 leader")
        for name, cfg in instances.items():
            check("working_directory" in cfg, f"{name} 有 working_directory")

    # scheduler.yaml
    print("\n── scheduler.yaml ──")
    sched = ROOT / "scheduler.yaml"
    check(sched.exists(), "scheduler.yaml 存在")
    if sched.exists():
        sd = yaml.safe_load(sched.read_text(encoding="utf-8"))
        jobs = sd.get("jobs", [])
        check(len(jobs) >= 2, f"≥ 2 jobs ({len(jobs)})")

    # agents/
    print("\n── agents/ ──")
    agents_dir = ROOT / "agents"
    check((agents_dir / "AGENTS.md").exists(), "agents/AGENTS.md")
    for agent in agents_dir.iterdir():
        if not agent.is_dir():
            continue
        name = agent.name
        print(f"\n  ── {name} ──")
        check((agent / "docs").is_dir(), f"{name}/docs/")
        check((agent / "output").is_dir(), f"{name}/output/")
        k = agent / "knowledge"
        check((k / "schema.md").exists(), f"{name}/knowledge/schema.md")
        check((k / "index.md").exists(), f"{name}/knowledge/index.md")
        check((k / "log.md").exists(), f"{name}/knowledge/log.md")
        check((k / "raw").is_dir(), f"{name}/knowledge/raw/")
        check((k / "wiki" / "overview.md").exists(), f"{name}/knowledge/wiki/overview.md")
        # .kiro
        kiro = agent / ".kiro"
        if kiro.exists():
            check(any(kiro.glob("agents/*.json")), f"{name}/.kiro/agents/*.json")
            check((kiro / "steering" / "SOUL.md").exists(), f"{name}/.kiro/steering/SOUL.md")
            check((kiro / "settings" / "mcp.json").exists(), f"{name}/.kiro/settings/mcp.json")

    # Project files
    print("\n── 專案檔案 ──")
    for f in ["README.md", "pyproject.toml", "requirements.txt", ".env.example", ".gitignore"]:
        check((ROOT / f).exists(), f)
    check((ROOT / "tasks" / "board.json").exists(), "tasks/board.json")
    check((ROOT / "skills").is_dir(), "skills/ 目錄")

    # Summary
    total = PASS + FAIL
    print(f"\n{'═' * 40}")
    print(f"結果：{PASS}/{total} 通過，{FAIL} 失敗")
    if FAIL == 0:
        print("✅ 結構驗證通過！")
    else:
        print("❌ 有缺失項目，請修復。")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()

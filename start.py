"""paddy-team-agent v1.1.0 — 使用 ark_team_agent 套件啟動。"""
from __future__ import annotations

import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from ark_team_agent.team import run_team

if __name__ == "__main__":
    try:
        asyncio.run(run_team(Path("team.yaml")))
    except KeyboardInterrupt:
        print("\n平台已停止。")

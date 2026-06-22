"""Ark Agent Platform — 入口。"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv
load_dotenv()

from bootstrap import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n平台已停止。")

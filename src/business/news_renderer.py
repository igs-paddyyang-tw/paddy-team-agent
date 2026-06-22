"""news_renderer — 將新聞列表渲染為 HTML 日報。"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from string import Template

TEMPLATE_PATH = Path("templates/tech-daily.html")
OUTPUT_DIR = Path("output")


async def render_daily(articles: list[dict], output_path: str = "") -> str:
    """渲染日報 HTML，回傳檔案路徑。"""
    if TEMPLATE_PATH.exists():
        tpl = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    else:
        tpl = Template(
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Daily $date</title></head>"
            "<body><h1>📰 Daily — $date</h1><ul>$items</ul></body></html>"
        )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    items_html = "\n".join(
        f'<li><a href="{a.get("url", "#")}">{a["title"]}</a> — {a.get("source", "")}</li>'
        for a in articles
    )

    html = tpl.safe_substitute(date=today, items=items_html, count=len(articles))
    out = Path(output_path) if output_path else OUTPUT_DIR / f"daily-{today}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)

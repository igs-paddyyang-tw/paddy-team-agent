"""news_scraper — 從多來源抓取科技新聞。"""
from __future__ import annotations

import logging
from pathlib import Path

import httpx
import yaml
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

CONFIG_PATH = Path("config/news_sources.yaml")


async def scrape_news(config_path: str | Path = CONFIG_PATH, limit: int = 10) -> list[dict]:
    """抓取新聞，回傳 [{title, url, source}]。"""
    cfg = Path(config_path)
    if not cfg.exists():
        return []
    sources = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    articles: list[dict] = []

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for source in sources.get("sources", []):
            try:
                r = await client.get(source["url"], headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code != 200:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                for el in soup.select(source.get("selector", "article"))[:5]:
                    title_el = el.select_one(source.get("title_sel", "h2, h3, a"))
                    link_el = el.select_one("a[href]")
                    if title_el:
                        articles.append({
                            "title": title_el.get_text(strip=True),
                            "url": link_el["href"] if link_el else "",
                            "source": source.get("name", ""),
                        })
            except Exception as e:
                log.debug("Scrape %s failed: %s", source.get("name"), e)

    return articles[:limit]

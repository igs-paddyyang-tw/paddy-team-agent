"""web_search — 快速網路搜尋（透過 Gemini grounding）。"""
from __future__ import annotations

import os
import httpx


async def web_search(query: str, limit: int = 5) -> list[dict]:
    """用 Gemini API 搜尋網路，回傳 [{title, snippet, url}]。"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return []

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    prompt = f"搜尋以下主題，列出前 {limit} 個相關結果（標題 + 一句摘要）：\n{query}"
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.post(url, json=body)
            if r.status_code != 200:
                return []
            data = r.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return [{"title": query, "snippet": text, "url": ""}]
        except Exception:
            return []

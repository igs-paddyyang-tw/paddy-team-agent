"""get_chat_id.py — 自動取得 Telegram Chat ID。

使用方式：
  1. 先對 Bot 發送任意訊息（如 /start）
  2. 執行：python scripts/get_chat_id.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("❌ 請先在 .env 中設定 TELEGRAM_BOT_TOKEN")
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    r = httpx.get(url, timeout=10)
    data = r.json()

    if not data.get("ok") or not data.get("result"):
        print("⚠️ 沒有收到任何訊息。請先對 Bot 發送 /start，再重新執行本腳本。")
        sys.exit(1)

    seen: set[int] = set()
    print("✅ 偵測到的 Chat ID：\n")
    for update in data["result"]:
        msg = update.get("message", {})
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        if chat_id and chat_id not in seen:
            seen.add(chat_id)
            name = chat.get("first_name", "") + " " + chat.get("last_name", "")
            chat_type = chat.get("type", "")
            print(f"  Chat ID: {chat_id}")
            print(f"  Name:    {name.strip()}")
            print(f"  Type:    {chat_type}")
            print()

    if seen:
        print(f"📋 將 Chat ID 填入 team.yaml 的 allowed_users 和 private_chat。")
    else:
        print("⚠️ 未偵測到 Chat ID。")


if __name__ == "__main__":
    main()

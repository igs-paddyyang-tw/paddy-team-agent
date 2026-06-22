"""Ark Telegram Bot — 入口 + handler 註冊。"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from telegram import BotCommand, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters,
)

from gateway.telegram.handlers.commands import (
    cmd_start, cmd_status, cmd_agents, cmd_board, cmd_costs, cmd_queue,
    cmd_assign, cmd_stop, cmd_retry, cmd_logs, cmd_help,
)
from gateway.telegram.handlers.messages import handle_message
from gateway.telegram.handlers.callbacks import handle_callback

log = logging.getLogger("telegram.bot")

BOT_COMMANDS = [
    BotCommand("start", "歡迎訊息"),
    BotCommand("status", "團隊即時狀態"),
    BotCommand("agents", "Agent 列表"),
    BotCommand("board", "看板摘要"),
    BotCommand("costs", "費用報告"),
    BotCommand("queue", "待處理佇列"),
    BotCommand("assign", "派工（/assign 描述）"),
    BotCommand("stop", "中斷 Agent"),
    BotCommand("retry", "重試任務"),
    BotCommand("logs", "查看日誌"),
    BotCommand("help", "指令說明"),
]


async def create_bot(api_base_url: str = "http://127.0.0.1:33333"):
    """建立並啟動 Telegram Bot。"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        log.warning("TELEGRAM_BOT_TOKEN 未設定，Bot 不啟動")
        return None

    app = ApplicationBuilder().token(token).build()

    # 注入 API base URL
    app.bot_data["api_base"] = api_base_url

    # 註冊指令
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("agents", cmd_agents))
    app.add_handler(CommandHandler("board", cmd_board))
    app.add_handler(CommandHandler("costs", cmd_costs))
    app.add_handler(CommandHandler("queue", cmd_queue))
    app.add_handler(CommandHandler("assign", cmd_assign))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("retry", cmd_retry))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("help", cmd_help))

    # Callback + 自然語言
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 設定指令列表
    await app.initialize()
    await app.bot.set_my_commands(BOT_COMMANDS)
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    log.info("Telegram Bot 已啟動")
    return app

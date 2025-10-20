# app/core/bot.py
"""Инициализация бота и диспетчера"""

import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

log = logging.getLogger("kudoaibot")

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

# Глобальные переменные для бота и диспетчера
bot = None
dp = None

def setup_bot_and_dispatcher():
    """Инициализация бота и диспетчера"""
    global bot, dp
    log.info("🔧 Инициализация бота и диспетчера...")
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    log.info("✅ Бот и диспетчер инициализированы")
    return bot, dp

# Инициализируем лениво - только при первом обращении
bot = None
dp = None

def get_bot():
    global bot, dp
    if bot is None or dp is None:
        bot, dp = setup_bot_and_dispatcher()
    return bot, dp


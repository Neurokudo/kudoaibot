# app/handlers/text.py
"""Обработчик текстовых сообщений"""

import logging
from aiogram import F
from aiogram.types import Message

from app.handlers.states import is_waiting_for_input
from app.handlers.video_handlers import handle_text_input
from app.handlers.commands import cmd_start
from app.core.bot import dp

log = logging.getLogger("kudoaibot")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text_message(message: Message):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    
    # Проверяем, ждёт ли бот ввода от этого пользователя
    if is_waiting_for_input(user_id):
        await handle_text_input(message)
    else:
        # Если не ждём ввода, показываем меню
        await cmd_start(message)


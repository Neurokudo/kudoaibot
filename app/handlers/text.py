# app/handlers/text.py
"""Обработчик текстовых сообщений"""

import logging
from aiogram import F
from aiogram.types import Message

from app.handlers.states import is_waiting_for_input
from app.handlers.video_handlers import handle_text_input
from app.handlers.commands import cmd_start
from app.core.bot import get_bot

log = logging.getLogger("kudoaibot")

def register_text_handlers():
    """Регистрация текстовых обработчиков"""
    bot, dp = get_bot()
    
    # Регистрируем обработчик фото (для примерочной)
    dp.message.register(handle_photo_message, F.photo)
    
    # Регистрируем обработчик текстовых сообщений (не команд)
    dp.message.register(handle_text_message, F.text & ~F.text.startswith("/"))
    
    # Регистрируем fallback для всех остальных типов сообщений
    dp.message.register(handle_fallback_message)

async def handle_photo_message(message: Message):
    """Обработка фото (для примерочной)"""
    user_id = message.from_user.id
    
    # Проверяем, ждёт ли бот фото для примерочной
    from app.handlers.tryon_handlers import handle_tryon_photo
    handled = await handle_tryon_photo(message)
    
    if not handled:
        # Если фото не для примерочной, показываем меню
        await message.answer(
            "📸 Фото получено, но я не понимаю, что с ним делать.\n\n"
            "Выберите раздел из меню:"
        )
        await cmd_start(message)

async def handle_text_message(message: Message):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    
    # Проверяем, ждёт ли бот ввода от этого пользователя
    if is_waiting_for_input(user_id):
        await handle_text_input(message)
    else:
        # Если не ждём ввода, показываем меню
        await cmd_start(message)

async def handle_fallback_message(message: Message):
    """Обработка всех остальных типов сообщений (фото, видео, стикеры и т.д.)"""
    log.info(f"Получено необработанное сообщение от пользователя {message.from_user.id}: {message.content_type}")
    
    # Просто показываем главное меню
    await cmd_start(message)


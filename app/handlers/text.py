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
    """Обработка текстовых сообщений с учетом режимов"""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Проверяем, ждёт ли бот ввода от этого пользователя
    if is_waiting_for_input(user_id):
        await handle_text_input(message)
        return
    
    # Проверяем состояние пользователя для новых режимов
    from app.handlers.states import get_user_state, set_user_state
    state = get_user_state(user_id)
    
    # Если пользователь ожидает промпт в новом режиме
    if hasattr(state, 'awaiting_prompt') and state.awaiting_prompt:
        mode = getattr(state, 'mode', 'manual')
        model = getattr(state, 'video_model', 'veo3')
        
        # Обрабатываем промпт в зависимости от режима
        if mode == "helper":
            # Умный помощник - улучшаем промпт через GPT
            from app.services.gpt_templates import improve_scene
            improved_prompt = improve_scene(text, "complex")
            await message.reply_text(
                f"🧠 **Улучшенный промпт:**\n\n{improved_prompt}\n\n"
                f"Генерирую видео..."
            )
            # Используем улучшенный промпт для генерации
            await handle_text_input(message, improved_prompt)
            
        elif mode == "neurokudo":
            # Neurokudo режим - специальная обработка
            from app.services.gpt_templates import improve_scene
            improved_prompt = improve_scene(text, "absurd")
            await message.reply_text(
                f"🔮 **Neurokudo промпт:**\n\n{improved_prompt}\n\n"
                f"Генерирую видео в стиле Neurokudo..."
            )
            await handle_text_input(message, improved_prompt)
            
        elif mode == "meme":
            # Мемный режим - быстрая генерация
            from app.services.gpt_templates import random_meme_scene, improve_scene
            if text.lower() in ["случайно", "случайная", "random", "мем"]:
                meme_prompt = random_meme_scene()
                await message.reply_text(
                    f"🤡 **Случайная мемная сцена:**\n\n{meme_prompt}\n\n"
                    f"Генерирую мем..."
                )
                await handle_text_input(message, meme_prompt)
            else:
                # Улучшаем пользовательский промпт для мемов
                meme_prompt = improve_scene(text, "absurd")
                await message.reply_text(
                    f"🤡 **Мемный промпт:**\n\n{meme_prompt}\n\n"
                    f"Генерирую мем..."
                )
                await handle_text_input(message, meme_prompt)
                
        elif mode == "manual":
            # Ручной режим - прямая генерация
            await message.reply_text("🎬 Генерирую видео...")
            await handle_text_input(message, text)
        
        # Сбрасываем состояние
        set_user_state(user_id, {})
        
    else:
        # Обычное сообщение - показываем главное меню
        await cmd_start(message)

async def handle_fallback_message(message: Message):
    """Обработка всех остальных типов сообщений (фото, видео, стикеры и т.д.)"""
    log.info(f"Получено необработанное сообщение от пользователя {message.from_user.id}: {message.content_type}")
    
    # Просто показываем главное меню
    await cmd_start(message)


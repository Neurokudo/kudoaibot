# app/services/ai_helper.py
"""AI помощник для улучшения промптов и генерации мемов"""

import os
import logging

log = logging.getLogger("ai_helper")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ленивая инициализация клиента (не при импорте)
_client = None

def get_openai_client():
    """Получить OpenAI клиента (ленивая инициализация)"""
    global _client
    
    if _client is None and OPENAI_API_KEY:
        try:
            from openai import OpenAI
            _client = OpenAI(api_key=OPENAI_API_KEY)
            log.info("✅ OpenAI клиент инициализирован")
        except Exception as e:
            log.error(f"❌ Ошибка инициализации OpenAI: {e}")
            _client = False  # Помечаем как неудачную попытку
    
    return _client if _client and _client is not False else None

def improve_prompt_with_gpt(user_input: str, mode: str = "helper") -> str:
    """
    Улучшить промпт с помощью GPT
    
    Args:
        user_input: Исходный текст от пользователя
        mode: Режим работы (helper, meme)
    
    Returns:
        Улучшенный промпт для VEO 3
    """
    client = get_openai_client()
    
    if not client:
        log.warning("OpenAI API key not set, returning original prompt")
        return user_input
    
    try:
        if mode == "meme":
            system_prompt = """Ты создаёшь короткие мемные видео промпты для VEO 3.
Пользователь даст тему или идею. Создай короткий (1-2 предложения), но яркий промпт для 6-секундного мемного видео.
Используй юмор, неожиданность, абсурд. Добавь детали про камеру, освещение, стиль.
Отвечай ТОЛЬКО промптом на английском, без пояснений."""
        else:  # helper
            system_prompt = """Ты - эксперт по созданию промптов для VEO 3 (Google's video generation model).
Пользователь даст краткую идею. Преобразуй её в детальный профессиональный промпт.

Структура хорошего промпта:
1. Главный объект/персонаж (внешность, одежда, действие)
2. Окружение (локация, время суток, погода)
3. Камера (угол, движение, тип съёмки)
4. Освещение (тип света, настроение)
5. Стиль (кинематограф, мультфильм, реализм и т.д.)

Отвечай ТОЛЬКО готовым промптом на английском, без объяснений и дополнительного текста."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.8 if mode == "meme" else 0.7,
            max_tokens=500
        )
        
        improved_prompt = response.choices[0].message.content.strip()
        log.info(f"GPT улучшил промпт ({mode}): {user_input[:50]}... -> {improved_prompt[:50]}...")
        
        return improved_prompt
        
    except Exception as e:
        log.error(f"Ошибка улучшения промпта: {e}")
        return user_input

async def improve_prompt_async(user_input: str, mode: str = "helper") -> str:
    """Асинхронная версия улучшения промпта"""
    import asyncio
    return await asyncio.to_thread(improve_prompt_with_gpt, user_input, mode)


# app/services/clients/sora_client.py
"""Клиент для SORA 2 через официальный OpenAI API"""

import os
import logging
import aiohttp
import json
from typing import Optional, Tuple

log = logging.getLogger("sora_client")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_SORA_URL = "https://api.openai.com/v1/videos/generations"
PUBLIC_URL = os.getenv("PUBLIC_URL")

async def create_sora_task(
    prompt: str,
    aspect_ratio: str = "9:16",
    duration: int = 5,
    user_id: Optional[int] = None
) -> Tuple[Optional[str], str]:
    """
    Создает задачу генерации видео через OpenAI SORA 2
    
    Args:
        prompt: Текстовое описание видео
        aspect_ratio: Соотношение сторон (9:16 или 16:9)
        duration: Длительность в секундах (до 20)
        user_id: ID пользователя для callback
    
    Returns:
        (task_id, status): ID задачи и статус ("success", "error", "demo_mode")
    """
    if not OPENAI_API_KEY:
        log.warning("⚠️ OPENAI_API_KEY not found, using demo mode")
        return None, "demo_mode"
    
    if not PUBLIC_URL:
        log.error("❌ PUBLIC_URL not found for callback")
        return None, "no_callback_url"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "KudoAiBot/2.0"
    }
    
    # Конвертируем aspect_ratio в формат OpenAI
    # OpenAI использует: "1:1", "16:9", "9:16"
    
    payload = {
        "model": "sora-1.0",  # Официальная модель OpenAI
        "prompt": prompt,
        "size": aspect_ratio,  # "9:16" или "16:9"
        "duration": min(duration, 20),  # Максимум 20 секунд
        "metadata": {
            "user_id": str(user_id) if user_id else "unknown"
        }
    }
    
    # Если доступен webhook, добавляем callback URL
    if PUBLIC_URL:
        payload["webhook_url"] = f"{PUBLIC_URL}/sora_callback"
    
    try:
        log.info(f"🎬 Creating SORA 2 task for user {user_id}: {prompt[:50]}...")
        log.info(f"📊 Parameters: aspect_ratio={aspect_ratio}, duration={duration}")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90)) as session:
            async with session.post(OPENAI_SORA_URL, headers=headers, json=payload) as response:
                response_text = await response.text()
                log.info(f"🎬 SORA 2 API response status: {response.status}")
                
                if response.status == 200 or response.status == 201:
                    data = json.loads(response_text)
                    
                    # OpenAI может вернуть сразу видео или ID задачи
                    task_id = data.get("id")
                    video_url = data.get("data", [{}])[0].get("url") if "data" in data else None
                    
                    if task_id:
                        log.info(f"✅ SORA 2 task created successfully: {task_id}")
                        return task_id, "success"
                    elif video_url:
                        # Если видео сразу готово
                        log.info(f"✅ SORA 2 video generated immediately: {video_url}")
                        return video_url, "immediate"
                    else:
                        log.error(f"❌ SORA 2 API unexpected response: {data}")
                        return None, "unexpected_response"
                        
                elif response.status == 402:
                    log.error("❌ SORA 2 API: Insufficient credits")
                    return None, "insufficient_credits"
                    
                elif response.status == 429:
                    log.error("❌ SORA 2 API: Rate limit exceeded")
                    return None, "rate_limit"
                    
                else:
                    log.error(f"❌ SORA 2 API HTTP error: {response.status} - {response_text}")
                    return None, f"http_error_{response.status}"
                    
    except aiohttp.ClientError as e:
        log.error(f"❌ Network error creating SORA 2 task: {e}")
        return None, "network_error"
    except Exception as e:
        log.error(f"❌ Unexpected error creating SORA 2 task: {e}")
        return None, "unknown_error"

def generate_video_sora2(
    prompt: str,
    duration: int = 5,
    aspect_ratio: str = "9:16",
    with_audio: bool = True
) -> dict:
    """
    Синхронная обёртка для генерации видео через SORA 2
    (использует asyncio под капотом)
    
    Args:
        prompt: Текстовое описание видео
        duration: Длительность в секундах (до 20)
        aspect_ratio: Соотношение сторон (9:16 или 16:9)
        with_audio: Генерировать ли аудио (всегда True для SORA 2)
    
    Returns:
        dict: {'videos': [{'file_path': str, 'url': str}]} или {'error': str}
    """
    log.info(f"SORA 2 генерация (sync): {prompt[:100]}...")
    
    # SORA 2 всегда генерирует со звуком
    # Если нужен синхронный вариант, используем asyncio.run
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    task_id, status = loop.run_until_complete(
        create_sora_task(prompt, aspect_ratio, duration)
    )
    
    if status == "success" or status == "immediate":
        return {
            "task_id": task_id,
            "status": status,
            "message": "Video generation started" if status == "success" else "Video ready"
        }
    else:
        return {
            "error": f"SORA 2 generation failed: {status}"
        }

async def generate_video_sora2_async(
    prompt: str,
    duration: int = 5,
    aspect_ratio: str = "9:16",
    with_audio: bool = True
) -> dict:
    """
    Асинхронная генерация видео через SORA 2
    
    Args:
        prompt: Текстовое описание видео
        duration: Длительность в секундах (до 20)
        aspect_ratio: Соотношение сторон (9:16 или 16:9)
        with_audio: Генерировать ли аудио (всегда True для SORA 2)
    
    Returns:
        dict: {'task_id': str, 'status': str} или {'error': str}
    """
    log.info(f"SORA 2 генерация (async): {prompt[:100]}...")
    
    task_id, status = await create_sora_task(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        duration=duration
    )
    
    if status == "success" or status == "immediate":
        return {
            "task_id": task_id,
            "status": status,
            "message": "Video generation started" if status == "success" else "Video ready"
        }
    elif status == "demo_mode":
        return {
            "error": "SORA 2 API key not configured. Please add OPENAI_API_KEY to environment."
        }
    else:
        return {
            "error": f"SORA 2 generation failed: {status}"
        }

def extract_user_from_metadata(metadata: dict) -> Optional[int]:
    """Извлекает user_id из метаданных callback"""
    try:
        user_id = metadata.get("user_id")
        if user_id:
            return int(user_id)
        return None
    except Exception as e:
        log.error(f"❌ Error extracting user_id from metadata: {e}")
        return None


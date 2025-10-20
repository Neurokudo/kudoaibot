# app/core/startup.py
"""Функции запуска и остановки бота"""

import os
import logging
import asyncio
from aiohttp import web
from aiogram import types

from app.db import database, subscriptions
from .bot import get_bot

log = logging.getLogger("kudoaibot")

async def setup_bot():
    """Инициализация бота и обработчиков"""
    log.info("🔧 Инициализация бота...")
    
    # Инициализация базы данных
    db_ok = await database.init_db()
    if not db_ok:
        log.error("❌ Не удалось инициализировать БД")
        raise RuntimeError("Не удалось инициализировать базу данных")
    
    log.info("✅ Подключение к базе данных установлено")
    log.info("✅ Таблицы базы данных созданы/обновлены")
    
    # Запуск задачи проверки истекших подписок
    asyncio.create_task(check_expired_subscriptions_task())
    log.info("✅ Задача проверки подписок запущена")
    
    # Запуск задачи очистки подписочных монет
    from app.services.coin_expiration import coin_expiration_task
    asyncio.create_task(coin_expiration_task())
    log.info("✅ Задача очистки подписочных монет запущена")

async def check_expired_subscriptions_task():
    """Фоновая задача проверки истекших подписок"""
    while True:
        try:
            await asyncio.sleep(3600)  # Проверяем каждый час
            expired_count = await subscriptions.deactivate_expired_subscriptions()
            if expired_count > 0:
                log.info(f"✅ Деактивировано {expired_count} истекших подписок")
        except Exception as e:
            log.error(f"❌ Ошибка проверки подписок: {e}")

async def graceful_shutdown():
    """Graceful shutdown функции"""
    log.info("🛑 Начинаем graceful shutdown...")
    
    try:
        bot, dp = get_bot()
        TELEGRAM_MODE = os.getenv("TELEGRAM_MODE", "webhook")
        
        if TELEGRAM_MODE == "webhook":
            try:
                await bot.delete_webhook()
                log.info("✅ Webhook удален")
            except Exception as e:
                log.error(f"❌ Ошибка удаления webhook: {e}")
        
        try:
            await bot.session.close()
            log.info("✅ Сессия бота закрыта")
        except Exception as e:
            log.error(f"❌ Ошибка закрытия сессии бота: {e}")
    except Exception as e:
        log.error(f"❌ Ошибка получения бота для shutdown: {e}")
    
    try:
        await database.close_db()
        log.info("✅ Соединение с БД закрыто")
    except Exception as e:
        log.error(f"❌ Ошибка закрытия БД: {e}")
    
    log.info("✅ Graceful shutdown завершен")

async def setup_web_app(dp, bot) -> web.Application:
    """Инициализация web приложения"""
    log.info("🔧 Инициализация web приложения...")
    
    app = web.Application()
    
    async def telegram_webhook(request):
        """Обработчик Telegram webhook"""
        try:
            data = await request.json()
            update = types.Update(**data)
            await dp.feed_update(bot, update)
            return web.Response(text="OK", status=200)
        except Exception as e:
            log.exception(f"Webhook error: {e}")
            return web.Response(text="Error", status=500)
    
    # Импортируем webhooks
    from app.webhooks.yookassa import yookassa_webhook
    from app.webhooks.sora2 import sora2_callback
    
    # Маршруты
    app.router.add_get('/', lambda _: web.Response(text="Bot is running ✅"))
    app.router.add_post('/webhook', telegram_webhook)
    app.router.add_post('/yookassa_webhook', yookassa_webhook)
    app.router.add_post('/sora_callback', sora2_callback)
    
    log.info("✅ Web приложение настроено")
    return app


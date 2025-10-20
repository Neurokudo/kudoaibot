# app/services/coin_expiration.py
"""
Cron-очистка подписочных монет через 30 дней
Фоновая задача для автоматического сгорания подписочных монеток
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict

from app.db import database
from app.core.bot import bot

log = logging.getLogger("coin_expiration")

async def expire_subscription_coins():
    """
    Удалить все подписочные монетки старше 30 дней
    
    Логика:
    1. Найти все активные подписки старше 30 дней
    2. Сбросить subscription_coins у этих пользователей
    3. Уведомить пользователей о сгорании
    """
    try:
        pool = database.get_db_pool()
        
        async with pool.acquire() as conn:
            # Находим пользователей с истёкшими подписками
            expired_users = await conn.fetch("""
                SELECT 
                    u.user_id,
                    u.subscription_coins,
                    u.permanent_coins,
                    s.end_date,
                    u.language
                FROM users u
                INNER JOIN subscriptions s ON u.user_id = s.user_id
                WHERE s.is_active = TRUE
                  AND s.end_date < NOW()
                  AND u.subscription_coins > 0
            """)
            
            if not expired_users:
                log.info("✅ Нет подписочных монет для сгорания")
                return 0
            
            expired_count = 0
            
            for user in expired_users:
                user_id = user['user_id']
                expired_coins = user['subscription_coins']
                permanent_coins = user['permanent_coins']
                language = user['language'] or 'ru'
                
                # Сбрасываем подписочные монетки
                await conn.execute("""
                    UPDATE users
                    SET subscription_coins = 0,
                        balance = COALESCE(permanent_coins, 0),
                        updated_at = NOW()
                    WHERE user_id = $1
                """, user_id)
                
                # Деактивируем подписку
                await conn.execute("""
                    UPDATE subscriptions
                    SET is_active = FALSE,
                        updated_at = NOW()
                    WHERE user_id = $1 AND is_active = TRUE
                """, user_id)
                
                expired_count += 1
                
                log.info(f"🔥 Сгорело {expired_coins} подписочных монет у user {user_id}")
                
                # Уведомляем пользователя
                try:
                    message_text = (
                        f"⏰ <b>Подписка истекла</b>\n\n"
                        f"🔥 Сгорело: {expired_coins} подписочных монет\n"
                        f"💚 Осталось: {permanent_coins} постоянных монет\n\n"
                        f"💡 Продлите подписку, чтобы получить новые монетки!\n"
                        f"Или используйте постоянные монетки для генераций."
                    )
                    
                    await bot.send_message(user_id, message_text, parse_mode="HTML")
                    log.info(f"✅ Уведомление отправлено user {user_id}")
                    
                except Exception as e:
                    log.error(f"❌ Ошибка отправки уведомления user {user_id}: {e}")
            
            log.info(f"🔥 Сгорело подписочных монет у {expired_count} пользователей")
            return expired_count
            
    except Exception as e:
        log.error(f"❌ Ошибка при очистке подписочных монет: {e}")
        return 0

async def check_expiring_soon(days_before: int = 3):
    """
    Проверить подписки, которые истекают в ближайшие N дней
    Отправить предупреждение пользователям
    
    Args:
        days_before: За сколько дней до истечения предупредить
    """
    try:
        pool = database.get_db_pool()
        
        async with pool.acquire() as conn:
            # Находим подписки, которые истекают скоро
            expiring_soon = await conn.fetch("""
                SELECT 
                    u.user_id,
                    u.subscription_coins,
                    s.end_date,
                    s.plan,
                    u.language
                FROM users u
                INNER JOIN subscriptions s ON u.user_id = s.user_id
                WHERE s.is_active = TRUE
                  AND s.end_date BETWEEN NOW() AND NOW() + INTERVAL '%s days'
                  AND u.subscription_coins > 0
            """ % days_before)
            
            for user in expiring_soon:
                user_id = user['user_id']
                coins = user['subscription_coins']
                end_date = user['end_date']
                plan = user['plan']
                language = user['language'] or 'ru'
                
                days_left = (end_date - datetime.now()).days
                
                try:
                    message_text = (
                        f"⚠️ <b>Подписка истекает через {days_left} дней!</b>\n\n"
                        f"📊 Тариф: {plan}\n"
                        f"🔥 Сгорит: {coins} подписочных монет\n"
                        f"📅 Дата истечения: {end_date.strftime('%d.%m.%Y')}\n\n"
                        f"💡 Продлите подписку, чтобы не потерять монетки!"
                    )
                    
                    await bot.send_message(user_id, message_text, parse_mode="HTML")
                    log.info(f"⚠️ Предупреждение отправлено user {user_id} ({days_left} дней)")
                    
                except Exception as e:
                    log.error(f"❌ Ошибка отправки предупреждения user {user_id}: {e}")
            
            log.info(f"⚠️ Отправлено {len(expiring_soon)} предупреждений об истечении")
            
    except Exception as e:
        log.error(f"❌ Ошибка проверки истекающих подписок: {e}")

async def coin_expiration_task():
    """
    Фоновая задача для проверки и очистки истёкших подписочных монет
    Запускается каждый час
    """
    while True:
        try:
            log.info("🔄 Проверка истёкших подписок...")
            
            # Очищаем истёкшие подписочные монетки
            expired = await expire_subscription_coins()
            
            if expired > 0:
                log.info(f"🔥 Очищено подписочных монет у {expired} пользователей")
            
            # Проверяем подписки, истекающие в ближайшие 3 дня
            await check_expiring_soon(days_before=3)
            
            # Ждём 1 час до следующей проверки
            await asyncio.sleep(3600)
            
        except Exception as e:
            log.error(f"❌ Ошибка в задаче очистки монет: {e}")
            await asyncio.sleep(3600)  # Ждём час даже при ошибке


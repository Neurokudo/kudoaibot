"""
Модуль для работы с подписками
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .database import execute_query, fetch_one, fetch_all

log = logging.getLogger("database.subscriptions")

async def create_subscription(
    user_id: int,
    plan: str,
    coins_granted: int,
    price_rub: int,
    duration_days: int = 30,
    payment_id: Optional[str] = None
) -> Dict[str, Any]:
    """Создать новую подписку"""
    try:
        end_date = datetime.now() + timedelta(days=duration_days)
        
        query = """
            INSERT INTO subscriptions 
            (user_id, plan, coins_granted, price_rub, end_date, payment_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        subscription = await fetch_one(
            query, user_id, plan, coins_granted, price_rub, end_date, payment_id
        )
        log.info(f"✅ Подписка создана: user={user_id}, plan={plan}, coins={coins_granted}")
        return subscription
    except Exception as e:
        log.error(f"❌ Ошибка создания подписки для {user_id}: {e}")
        raise

async def get_active_subscription(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить активную подписку пользователя"""
    try:
        query = """
            SELECT * FROM subscriptions
            WHERE user_id = $1 
            AND is_active = TRUE 
            AND end_date > CURRENT_TIMESTAMP
            ORDER BY end_date DESC
            LIMIT 1
        """
        return await fetch_one(query, user_id)
    except Exception as e:
        log.error(f"❌ Ошибка получения подписки {user_id}: {e}")
        return None

async def deactivate_subscription(subscription_id: int) -> bool:
    """Деактивировать подписку"""
    try:
        query = """
            UPDATE subscriptions
            SET is_active = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """
        await execute_query(query, subscription_id)
        log.info(f"✅ Подписка {subscription_id} деактивирована")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка деактивации подписки {subscription_id}: {e}")
        return False

async def deactivate_expired_subscriptions() -> int:
    """Деактивировать все истекшие подписки"""
    try:
        query = """
            UPDATE subscriptions
            SET is_active = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE is_active = TRUE 
            AND end_date <= CURRENT_TIMESTAMP
            RETURNING id, user_id
        """
        expired = await fetch_all(query)
        
        if expired:
            log.info(f"✅ Деактивировано {len(expired)} истекших подписок")
            
            # Обновляем тарифы пользователей на free
            for sub in expired:
                await execute_query(
                    "UPDATE users SET plan = 'free', updated_at = CURRENT_TIMESTAMP WHERE user_id = $1",
                    sub['user_id']
                )
        
        return len(expired)
    except Exception as e:
        log.error(f"❌ Ошибка деактивации истекших подписок: {e}")
        return 0

async def check_subscription_status(user_id: int) -> Dict[str, Any]:
    """Проверить статус подписки пользователя"""
    try:
        subscription = await get_active_subscription(user_id)
        
        if not subscription:
            return {
                "has_active": False,
                "plan": "free",
                "expires_at": None,
                "days_left": 0
            }
        
        end_date = subscription['end_date']
        days_left = (end_date - datetime.now()).days
        
        return {
            "has_active": True,
            "plan": subscription['plan'],
            "expires_at": end_date,
            "days_left": max(0, days_left),
            "subscription_id": subscription['id']
        }
    except Exception as e:
        log.error(f"❌ Ошибка проверки статуса подписки {user_id}: {e}")
        return {
            "has_active": False,
            "plan": "free",
            "expires_at": None,
            "days_left": 0
        }

async def get_all_subscriptions(user_id: int) -> List[Dict[str, Any]]:
    """Получить все подписки пользователя"""
    try:
        query = """
            SELECT * FROM subscriptions
            WHERE user_id = $1
            ORDER BY created_at DESC
        """
        return await fetch_all(query, user_id)
    except Exception as e:
        log.error(f"❌ Ошибка получения подписок {user_id}: {e}")
        return []

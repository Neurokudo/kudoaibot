"""
Модуль для работы с транзакциями
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .database import execute_query, fetch_one, fetch_all

log = logging.getLogger("database.transactions")

async def create_transaction(
    user_id: int,
    transaction_type: str,
    coins_delta: int,
    balance_before: int,
    balance_after: int,
    feature: Optional[str] = None,
    note: Optional[str] = None,
    payment_id: Optional[str] = None
) -> Dict[str, Any]:
    """Создать новую транзакцию"""
    try:
        query = """
            INSERT INTO transactions 
            (user_id, transaction_type, feature, coins_delta, balance_before, balance_after, note, payment_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
        """
        transaction = await fetch_one(
            query, user_id, transaction_type, feature, coins_delta, 
            balance_before, balance_after, note, payment_id
        )
        
        log.info(
            f"✅ Транзакция создана: user={user_id}, type={transaction_type}, "
            f"delta={coins_delta:+d}, balance={balance_before}→{balance_after}"
        )
        return transaction
    except Exception as e:
        log.error(f"❌ Ошибка создания транзакции для {user_id}: {e}")
        raise

async def get_user_transactions(
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Получить транзакции пользователя"""
    try:
        query = """
            SELECT * FROM transactions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """
        return await fetch_all(query, user_id, limit, offset)
    except Exception as e:
        log.error(f"❌ Ошибка получения транзакций {user_id}: {e}")
        return []

async def get_user_transaction_history(
    user_id: int,
    days: int = 30
) -> List[Dict[str, Any]]:
    """Получить историю транзакций за последние N дней"""
    try:
        since_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT * FROM transactions
            WHERE user_id = $1 AND created_at >= $2
            ORDER BY created_at DESC
        """
        return await fetch_all(query, user_id, since_date)
    except Exception as e:
        log.error(f"❌ Ошибка получения истории транзакций {user_id}: {e}")
        return []

async def get_transaction_by_payment_id(payment_id: str) -> Optional[Dict[str, Any]]:
    """Получить транзакцию по ID платежа"""
    try:
        query = """
            SELECT * FROM transactions
            WHERE payment_id = $1
            ORDER BY created_at DESC
            LIMIT 1
        """
        return await fetch_one(query, payment_id)
    except Exception as e:
        log.error(f"❌ Ошибка получения транзакции по payment_id {payment_id}: {e}")
        return None

async def get_spending_stats(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Получить статистику трат пользователя"""
    try:
        since_date = datetime.now() - timedelta(days=days)
        
        # Общая статистика
        query = """
            SELECT 
                SUM(CASE WHEN coins_delta < 0 THEN ABS(coins_delta) ELSE 0 END) as total_spent,
                SUM(CASE WHEN coins_delta > 0 THEN coins_delta ELSE 0 END) as total_received,
                COUNT(CASE WHEN coins_delta < 0 THEN 1 END) as spend_count,
                COUNT(CASE WHEN coins_delta > 0 THEN 1 END) as receive_count
            FROM transactions
            WHERE user_id = $1 AND created_at >= $2
        """
        stats = await fetch_one(query, user_id, since_date)
        
        # Статистика по типам функций
        query_features = """
            SELECT 
                feature,
                COUNT(*) as usage_count,
                SUM(ABS(coins_delta)) as total_coins
            FROM transactions
            WHERE user_id = $1 AND created_at >= $2 AND feature IS NOT NULL AND coins_delta < 0
            GROUP BY feature
            ORDER BY total_coins DESC
        """
        features = await fetch_all(query_features, user_id, since_date)
        
        return {
            "total_spent": stats['total_spent'] or 0,
            "total_received": stats['total_received'] or 0,
            "spend_count": stats['spend_count'] or 0,
            "receive_count": stats['receive_count'] or 0,
            "features": features,
            "period_days": days
        }
    except Exception as e:
        log.error(f"❌ Ошибка получения статистики трат {user_id}: {e}")
        return {
            "total_spent": 0,
            "total_received": 0,
            "spend_count": 0,
            "receive_count": 0,
            "features": [],
            "period_days": days
        }

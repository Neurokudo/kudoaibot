"""
Модуль для работы с пользователями
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .database import execute_query, fetch_one, fetch_all

log = logging.getLogger("database.users")

async def create_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """Создать нового пользователя"""
    try:
        query = """
            INSERT INTO users (user_id, username, first_name, last_name, language, balance, plan)
            VALUES ($1, $2, $3, $4, $5, 0, 'free')
            ON CONFLICT (user_id) DO UPDATE
            SET username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING *
        """
        user = await fetch_one(query, user_id, username, first_name, last_name, language)
        log.info(f"✅ Пользователь создан/обновлен: {user_id}")
        return user
    except Exception as e:
        log.error(f"❌ Ошибка создания пользователя {user_id}: {e}")
        raise

async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить пользователя по ID"""
    try:
        query = "SELECT * FROM users WHERE user_id = $1"
        return await fetch_one(query, user_id)
    except Exception as e:
        log.error(f"❌ Ошибка получения пользователя {user_id}: {e}")
        return None

async def update_user_balance(user_id: int, coins_delta: int) -> bool:
    """Обновить баланс пользователя"""
    try:
        query = """
            UPDATE users
            SET balance = balance + $2,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
            RETURNING balance
        """
        result = await fetch_one(query, user_id, coins_delta)
        if result:
            log.info(f"✅ Баланс пользователя {user_id} обновлен: {coins_delta:+d} → {result['balance']}")
            return True
        return False
    except Exception as e:
        log.error(f"❌ Ошибка обновления баланса {user_id}: {e}")
        return False

async def update_user_plan(user_id: int, plan: str) -> bool:
    """Обновить тариф пользователя"""
    try:
        query = """
            UPDATE users
            SET plan = $2,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
        """
        await execute_query(query, user_id, plan)
        log.info(f"✅ Тариф пользователя {user_id} обновлен: {plan}")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка обновления тарифа {user_id}: {e}")
        return False

async def get_user_balance(user_id: int) -> int:
    """Получить баланс пользователя"""
    try:
        query = "SELECT balance FROM users WHERE user_id = $1"
        result = await fetch_one(query, user_id)
        return result['balance'] if result else 0
    except Exception as e:
        log.error(f"❌ Ошибка получения баланса {user_id}: {e}")
        return 0

async def set_user_balance(user_id: int, balance: int) -> bool:
    """Установить точный баланс пользователя (админ функция)"""
    try:
        query = """
            UPDATE users
            SET balance = $2,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
        """
        await execute_query(query, user_id, balance)
        log.info(f"✅ Баланс пользователя {user_id} установлен: {balance}")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка установки баланса {user_id}: {e}")
        return False

async def block_user(user_id: int) -> bool:
    """Заблокировать пользователя"""
    try:
        query = """
            UPDATE users
            SET is_blocked = TRUE,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
        """
        await execute_query(query, user_id)
        log.info(f"✅ Пользователь {user_id} заблокирован")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка блокировки пользователя {user_id}: {e}")
        return False

async def unblock_user(user_id: int) -> bool:
    """Разблокировать пользователя"""
    try:
        query = """
            UPDATE users
            SET is_blocked = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
        """
        await execute_query(query, user_id)
        log.info(f"✅ Пользователь {user_id} разблокирован")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка разблокировки пользователя {user_id}: {e}")
        return False

async def is_user_blocked(user_id: int) -> bool:
    """Проверить, заблокирован ли пользователь"""
    try:
        query = "SELECT is_blocked FROM users WHERE user_id = $1"
        result = await fetch_one(query, user_id)
        return result['is_blocked'] if result else False
    except Exception as e:
        log.error(f"❌ Ошибка проверки блокировки {user_id}: {e}")
        return False

async def update_user_language(user_id: int, language: str) -> bool:
    """Обновить язык пользователя"""
    try:
        query = """
            UPDATE users 
            SET language = $2, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
        """
        await execute_query(query, user_id, language)
        log.info(f"✅ Язык пользователя {user_id} обновлен на {language}")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка обновления языка {user_id}: {e}")
        return False

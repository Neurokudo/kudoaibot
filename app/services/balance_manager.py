"""
Централизованный менеджер баланса
Единая точка для всех операций с монетками
"""
import logging
from typing import Dict, Any
from app.db import users, transactions

log = logging.getLogger("balance_manager")

class InsufficientFundsError(Exception):
    """Исключение при недостатке средств"""
    pass

async def get_balance(user_id: int) -> int:
    """Получить текущий баланс пользователя"""
    try:
        balance = await users.get_user_balance(user_id)
        return balance
    except Exception as e:
        log.error(f"Ошибка получения баланса {user_id}: {e}")
        return 0

async def add_coins(
    user_id: int,
    amount: int,
    transaction_type: str = "topup",
    feature: str = None,
    note: str = None,
    payment_id: str = None
) -> int:
    """
    Добавить монетки пользователю
    
    Args:
        user_id: ID пользователя
        amount: Количество монеток
        transaction_type: Тип транзакции (subscription, topup, bonus, refund, admin)
        feature: Название функции/операции
        note: Дополнительное описание
        payment_id: ID платежа
        
    Returns:
        Новый баланс
    """
    if amount <= 0:
        raise ValueError(f"Количество должно быть положительным: {amount}")
    
    try:
        # Получаем текущий баланс
        old_balance = await get_balance(user_id)
        
        # Обновляем баланс
        success = await users.update_user_balance(user_id, amount)
        if not success:
            raise Exception("Не удалось обновить баланс в БД")
        
        new_balance = old_balance + amount
        
        # Создаем транзакцию
        await transactions.create_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            coins_delta=amount,
            balance_before=old_balance,
            balance_after=new_balance,
            feature=feature,
            note=note,
            payment_id=payment_id
        )
        
        log.info(f"✅ [БАЛАНС +] user={user_id} +{amount} → {new_balance} ({transaction_type})")
        return new_balance
        
    except Exception as e:
        log.error(f"❌ Ошибка добавления монеток {user_id}: {e}")
        raise

async def spend_coins(
    user_id: int,
    amount: int,
    feature: str,
    note: str = None
) -> int:
    """
    Потратить монетки пользователя
    
    Args:
        user_id: ID пользователя
        amount: Количество монеток
        feature: Название функции (video_8s_audio, virtual_tryon и т.д.)
        note: Дополнительное описание
        
    Returns:
        Новый баланс
        
    Raises:
        InsufficientFundsError: Если недостаточно средств
    """
    if amount <= 0:
        raise ValueError(f"Количество должно быть положительным: {amount}")
    
    try:
        # Получаем текущий баланс
        old_balance = await get_balance(user_id)
        
        # Проверяем достаточность средств
        if old_balance < amount:
            raise InsufficientFundsError(
                f"Недостаточно монеток: нужно {amount}, доступно {old_balance}"
            )
        
        # Списываем монетки
        success = await users.update_user_balance(user_id, -amount)
        if not success:
            raise Exception("Не удалось обновить баланс в БД")
        
        new_balance = old_balance - amount
        
        # Создаем транзакцию
        await transactions.create_transaction(
            user_id=user_id,
            transaction_type="spend",
            coins_delta=-amount,
            balance_before=old_balance,
            balance_after=new_balance,
            feature=feature,
            note=note or f"Использование: {feature}"
        )
        
        log.info(f"✅ [БАЛАНС -] user={user_id} -{amount} → {new_balance} ({feature})")
        return new_balance
        
    except InsufficientFundsError:
        raise
    except Exception as e:
        log.error(f"❌ Ошибка списания монеток {user_id}: {e}")
        raise

async def can_afford(user_id: int, amount: int) -> bool:
    """Проверить, может ли пользователь позволить себе операцию"""
    try:
        balance = await get_balance(user_id)
        return balance >= amount
    except Exception as e:
        log.error(f"❌ Ошибка проверки возможности оплаты {user_id}: {e}")
        return False

async def set_balance(
    user_id: int,
    new_balance: int,
    admin_note: str = "Admin operation"
) -> int:
    """
    Установить точный баланс (админ функция)
    
    Args:
        user_id: ID пользователя
        new_balance: Новый баланс
        admin_note: Заметка администратора
        
    Returns:
        Новый баланс
    """
    try:
        old_balance = await get_balance(user_id)
        delta = new_balance - old_balance
        
        if delta == 0:
            log.info(f"Баланс {user_id} не изменился: {old_balance}")
            return old_balance
        
        # Устанавливаем новый баланс
        success = await users.set_user_balance(user_id, new_balance)
        if not success:
            raise Exception("Не удалось установить баланс в БД")
        
        # Создаем транзакцию
        await transactions.create_transaction(
            user_id=user_id,
            transaction_type="admin",
            coins_delta=delta,
            balance_before=old_balance,
            balance_after=new_balance,
            feature="admin_set_balance",
            note=f"Админ: {admin_note}"
        )
        
        log.info(f"✅ [БАЛАНС =] user={user_id} {old_balance} → {new_balance} (admin)")
        return new_balance
        
    except Exception as e:
        log.error(f"❌ Ошибка установки баланса {user_id}: {e}")
        raise

async def get_user_summary(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Получить сводку по пользователю"""
    try:
        balance = await get_balance(user_id)
        stats = await transactions.get_spending_stats(user_id, days=days)
        
        return {
            "user_id": user_id,
            "current_balance": balance,
            "stats": stats
        }
    except Exception as e:
        log.error(f"❌ Ошибка получения сводки {user_id}: {e}")
        return {
            "user_id": user_id,
            "current_balance": 0,
            "stats": {}
        }

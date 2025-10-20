# app/services/dual_balance.py
"""
Система двух балансов монеток:
🟢 Подписочные (сгорают через 30 дней)
🟣 Купленные/Постоянные (не сгорают никогда)

Приоритет списания: сначала подписочные, потом постоянные
"""

import logging
from typing import Dict, Tuple
from datetime import datetime

from app.db import database

log = logging.getLogger("dual_balance")

async def get_user_dual_balance(user_id: int) -> Dict[str, int]:
    """
    Получить оба баланса пользователя
    
    Returns:
        {
            'subscription_coins': int,  # 🟢 Подписочные
            'permanent_coins': int,     # 🟣 Постоянные
            'total': int                # Общий баланс
        }
    """
    pool = database.get_db_pool()
    if not pool:
        raise RuntimeError("Database pool not initialized")
    
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT 
                COALESCE(subscription_coins, 0) as subscription_coins,
                COALESCE(permanent_coins, 0) as permanent_coins
            FROM users
            WHERE user_id = $1
        """, user_id)
        
        if not result:
            return {
                'subscription_coins': 0,
                'permanent_coins': 0,
                'total': 0
            }
        
        return {
            'subscription_coins': result['subscription_coins'],
            'permanent_coins': result['permanent_coins'],
            'total': result['subscription_coins'] + result['permanent_coins']
        }

async def deduct_coins(user_id: int, coins: int) -> Dict:
    """
    Списать монетки с приоритетом: сначала подписочные, потом постоянные
    
    Args:
        user_id: ID пользователя
        coins: Сколько монеток списать
    
    Returns:
        {
            'success': bool,
            'deducted_from_subscription': int,
            'deducted_from_permanent': int,
            'new_balance': dict
        }
    """
    pool = database.get_db_pool()
    if not pool:
        raise RuntimeError("Database pool not initialized")
    
    async with pool.acquire() as conn:
        # Получаем текущие балансы
        user = await conn.fetchrow("""
            SELECT subscription_coins, permanent_coins
            FROM users
            WHERE user_id = $1
        """, user_id)
        
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        sub_coins = user['subscription_coins'] or 0
        perm_coins = user['permanent_coins'] or 0
        total = sub_coins + perm_coins
        
        if total < coins:
            return {
                'success': False,
                'error': 'Insufficient balance',
                'needed': coins,
                'available': total
            }
        
        # Списываем сначала с подписочных
        deducted_sub = min(coins, sub_coins)
        remaining = coins - deducted_sub
        
        # Если не хватило подписочных, списываем с постоянных
        deducted_perm = min(remaining, perm_coins) if remaining > 0 else 0
        
        new_sub = sub_coins - deducted_sub
        new_perm = perm_coins - deducted_perm
        
        # Обновляем балансы
        await conn.execute("""
            UPDATE users
            SET subscription_coins = $2,
                permanent_coins = $3,
                balance = $4,
                updated_at = NOW()
            WHERE user_id = $1
        """, user_id, new_sub, new_perm, new_sub + new_perm)
        
        log.info(
            f"💰 Списано {coins} монет у user {user_id}: "
            f"{deducted_sub} подписочных + {deducted_perm} постоянных"
        )
        
        return {
            'success': True,
            'deducted_from_subscription': deducted_sub,
            'deducted_from_permanent': deducted_perm,
            'new_balance': {
                'subscription_coins': new_sub,
                'permanent_coins': new_perm,
                'total': new_sub + new_perm
            }
        }

async def add_subscription_coins(user_id: int, coins: int) -> Dict:
    """
    Добавить подписочные монетки (сгорают через 30 дней)
    
    Args:
        user_id: ID пользователя
        coins: Сколько монеток добавить
    
    Returns:
        {'success': bool, 'new_balance': dict}
    """
    pool = database.get_db_pool()
    if not pool:
        raise RuntimeError("Database pool not initialized")
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET subscription_coins = COALESCE(subscription_coins, 0) + $2,
                balance = COALESCE(balance, 0) + $2,
                updated_at = NOW()
            WHERE user_id = $1
        """, user_id, coins)
        
        # Получаем новый баланс
        balance = await get_user_dual_balance(user_id)
        
        log.info(f"🟢 Добавлено {coins} подписочных монет user {user_id}")
        
        return {
            'success': True,
            'coins_added': coins,
            'new_balance': balance
        }

async def add_permanent_coins(user_id: int, coins: int) -> Dict:
    """
    Добавить постоянные монетки (НЕ сгорают)
    
    Args:
        user_id: ID пользователя
        coins: Сколько монеток добавить
    
    Returns:
        {'success': bool, 'new_balance': dict}
    """
    pool = database.get_db_pool()
    if not pool:
        raise RuntimeError("Database pool not initialized")
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET permanent_coins = COALESCE(permanent_coins, 0) + $2,
                balance = COALESCE(balance, 0) + $2,
                updated_at = NOW()
            WHERE user_id = $1
        """, user_id, coins)
        
        # Получаем новый баланс
        balance = await get_user_dual_balance(user_id)
        
        log.info(f"🟣 Добавлено {coins} постоянных монет user {user_id}")
        
        return {
            'success': True,
            'coins_added': coins,
            'new_balance': balance
        }

async def reset_subscription_coins(user_id: int) -> Dict:
    """
    Сбросить подписочные монетки (при истечении подписки)
    
    Args:
        user_id: ID пользователя
    
    Returns:
        {'success': bool, 'coins_removed': int}
    """
    pool = database.get_db_pool()
    if not pool:
        raise RuntimeError("Database pool not initialized")
    
    async with pool.acquire() as conn:
        # Получаем текущие подписочные монетки
        old_sub = await conn.fetchval("""
            SELECT COALESCE(subscription_coins, 0)
            FROM users
            WHERE user_id = $1
        """, user_id)
        
        if old_sub and old_sub > 0:
            # Сбрасываем подписочные, пересчитываем общий баланс
            await conn.execute("""
                UPDATE users
                SET subscription_coins = 0,
                    balance = COALESCE(permanent_coins, 0),
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id)
            
            log.info(f"🔥 Сгорело {old_sub} подписочных монет у user {user_id}")
            
            return {
                'success': True,
                'coins_removed': old_sub
            }
        
        return {
            'success': True,
            'coins_removed': 0
        }

async def check_can_spend(user_id: int, coins: int) -> Dict:
    """
    Проверить, достаточно ли монеток для операции
    
    Args:
        user_id: ID пользователя
        coins: Сколько нужно монеток
    
    Returns:
        {
            'can_spend': bool,
            'current_balance': dict,
            'needed': int
        }
    """
    balance = await get_user_dual_balance(user_id)
    
    return {
        'can_spend': balance['total'] >= coins,
        'current_balance': balance,
        'needed': coins,
        'shortage': max(0, coins - balance['total'])
    }

def format_balance_display(balance: Dict, days_left: int = None) -> str:
    """
    Форматировать баланс для отображения пользователю
    
    Args:
        balance: Словарь с балансами
        days_left: Дней до истечения подписки (опционально)
    
    Returns:
        Текст для отображения
    """
    from app.utils.formatting import format_coins
    
    total = balance['total']
    sub = balance['subscription_coins']
    perm = balance['permanent_coins']
    
    lines = []
    
    if sub > 0 and perm > 0:
        lines.append(f"💰 <b>Баланс: {format_coins(total)}</b>")
        lines.append(f"├ 🟢 Подписочные: {format_coins(sub, short=True)}")
        lines.append(f"└ 🟣 Постоянные: {format_coins(perm, short=True)}")
    elif sub > 0:
        lines.append(f"💰 <b>Баланс: {format_coins(total)}</b>")
        lines.append(f"└ 🟢 Подписочные монетки")
    elif perm > 0:
        lines.append(f"💰 <b>Баланс: {format_coins(total)}</b>")
        lines.append(f"└ 🟣 Постоянные монетки")
    else:
        lines.append(f"💰 <b>Баланс: 0 монеток</b>")
    
    # Добавляем информацию о подписке если есть
    if days_left is not None and days_left > 0:
        lines.append(f"🔋 <b>Осталось по подписке: {days_left} дней</b>")
    
    lines.append(f"📊 <b>Итого монеток: {total}</b>")
    
    return "\n".join(lines)


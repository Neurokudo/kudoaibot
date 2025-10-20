"""
Система биллинга
Управление платежами, подписками и доступом к функциям
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.db import users, subscriptions
from app.config.pricing import (
    get_tariff_info,
    get_feature_cost,
    TARIFFS
)
from . import balance_manager

log = logging.getLogger("billing")

async def check_access(user_id: int, feature: str) -> Dict[str, Any]:
    """
    Проверить доступ пользователя к функции
    
    Args:
        user_id: ID пользователя
        feature: Название функции
        
    Returns:
        Dict с результатом проверки
    """
    try:
        # Проверяем, не заблокирован ли пользователь
        is_blocked = await users.is_user_blocked(user_id)
        if is_blocked:
            return {
                "access": False,
                "reason": "user_blocked",
                "message": "❌ Ваш аккаунт заблокирован"
            }
        
        # Получаем стоимость функции
        cost = get_feature_cost(feature)
        
        # Проверяем баланс
        balance = await balance_manager.get_balance(user_id)
        
        if balance < cost:
            return {
                "access": False,
                "reason": "insufficient_funds",
                "message": f"❌ Недостаточно монеток\nНужно: {cost}\nДоступно: {balance}",
                "balance": balance,
                "cost": cost
            }
        
        return {
            "access": True,
            "reason": "ok",
            "message": "✅ Доступ разрешен",
            "balance": balance,
            "cost": cost
        }
        
    except Exception as e:
        log.error(f"❌ Ошибка проверки доступа {user_id} к {feature}: {e}")
        return {
            "access": False,
            "reason": "error",
            "message": "❌ Ошибка проверки доступа"
        }

async def deduct_coins_for_feature(
    user_id: int,
    feature: str,
    custom_cost: Optional[int] = None
) -> Dict[str, Any]:
    """
    Списать монетки за использование функции
    
    Args:
        user_id: ID пользователя
        feature: Название функции
        custom_cost: Пользовательская стоимость (если None, берется из конфига)
        
    Returns:
        Dict с результатом операции
    """
    try:
        cost = custom_cost if custom_cost is not None else get_feature_cost(feature)
        
        # Проверяем доступ
        access_check = await check_access(user_id, feature)
        if not access_check["access"]:
            return {
                "success": False,
                "reason": access_check["reason"],
                "message": access_check["message"]
            }
        
        # Списываем монетки
        try:
            new_balance = await balance_manager.spend_coins(
                user_id=user_id,
                amount=cost,
                feature=feature
            )
            
            return {
                "success": True,
                "coins_spent": cost,
                "balance_after": new_balance,
                "message": f"✅ Списано {cost} монеток. Остаток: {new_balance}"
            }
            
        except balance_manager.InsufficientFundsError as e:
            return {
                "success": False,
                "reason": "insufficient_funds",
                "message": str(e)
            }
            
    except Exception as e:
        log.error(f"❌ Ошибка списания монеток {user_id} для {feature}: {e}")
        return {
            "success": False,
            "reason": "error",
            "message": "❌ Ошибка списания монеток"
        }

async def process_subscription_payment(
    user_id: int,
    tariff_name: str,
    payment_id: str
) -> Dict[str, Any]:
    """
    Обработать оплату подписки
    
    Args:
        user_id: ID пользователя
        tariff_name: Название тарифа
        payment_id: ID платежа
        
    Returns:
        Dict с результатом обработки
    """
    try:
        # Получаем информацию о тарифе
        tariff = get_tariff_info(tariff_name)
        if not tariff:
            return {
                "success": False,
                "reason": "tariff_not_found",
                "message": f"❌ Тариф {tariff_name} не найден"
            }
        
        # Создаем подписку
        subscription = await subscriptions.create_subscription(
            user_id=user_id,
            plan=tariff_name,
            coins_granted=tariff.coins,
            price_rub=tariff.price_rub,
            duration_days=tariff.duration_days,
            payment_id=payment_id
        )
        
        # Добавляем монетки
        new_balance = await balance_manager.add_coins(
            user_id=user_id,
            amount=tariff.coins,
            transaction_type="subscription",
            feature=f"subscription_{tariff_name}",
            note=f"Подписка {tariff.title} ({tariff.duration_days} дней)",
            payment_id=payment_id
        )
        
        # Обновляем план пользователя
        await users.update_user_plan(user_id, tariff_name)
        
        log.info(
            f"✅ Подписка активирована: user={user_id}, plan={tariff_name}, "
            f"coins={tariff.coins}, balance={new_balance}"
        )
        
        return {
            "success": True,
            "subscription": subscription,
            "coins_added": tariff.coins,
            "balance": new_balance,
            "message": (
                f"✅ Подписка {tariff.icon} <b>{tariff.title}</b> активирована!\n"
                f"Добавлено {tariff.coins} монеток\n"
                f"Ваш баланс: {new_balance} монеток"
            )
        }
        
    except Exception as e:
        log.error(f"❌ Ошибка обработки подписки {user_id}: {e}")
        return {
            "success": False,
            "reason": "error",
            "message": "❌ Ошибка обработки подписки"
        }

async def process_topup_payment(
    user_id: int,
    coins: int,
    price_rub: int,
    payment_id: str,
    bonus_coins: int = 0
) -> Dict[str, Any]:
    """
    Обработать оплату пополнения
    
    Args:
        user_id: ID пользователя
        coins: Количество монеток
        price_rub: Цена в рублях
        payment_id: ID платежа
        bonus_coins: Бонусные монетки
        
    Returns:
        Dict с результатом обработки
    """
    try:
        total_coins = coins + bonus_coins
        
        # Добавляем монетки
        new_balance = await balance_manager.add_coins(
            user_id=user_id,
            amount=total_coins,
            transaction_type="topup",
            feature="topup",
            note=f"Пополнение: {coins} монеток" + (f" + {bonus_coins} бонус" if bonus_coins > 0 else ""),
            payment_id=payment_id
        )
        
        log.info(
            f"✅ Пополнение обработано: user={user_id}, coins={total_coins}, "
            f"balance={new_balance}"
        )
        
        message = f"✅ Пополнение успешно!\nДобавлено {coins} монеток"
        if bonus_coins > 0:
            message += f" + {bonus_coins} бонусных"
        message += f"\nВаш баланс: {new_balance} монеток"
        
        return {
            "success": True,
            "coins_added": total_coins,
            "balance": new_balance,
            "message": message
        }
        
    except Exception as e:
        log.error(f"❌ Ошибка обработки пополнения {user_id}: {e}")
        return {
            "success": False,
            "reason": "error",
            "message": "❌ Ошибка обработки пополнения"
        }

async def get_user_subscription_status(user_id: int) -> Dict[str, Any]:
    """Получить статус подписки пользователя"""
    try:
        status = await subscriptions.check_subscription_status(user_id)
        balance = await balance_manager.get_balance(user_id)
        
        return {
            **status,
            "balance": balance
        }
    except Exception as e:
        log.error(f"❌ Ошибка получения статуса подписки {user_id}: {e}")
        return {
            "has_active": False,
            "plan": "free",
            "balance": 0,
            "expires_at": None,
            "days_left": 0
        }

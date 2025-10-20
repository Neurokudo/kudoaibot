"""
Интеграция с YooKassa для приема платежей
"""
import os
import logging
import uuid
from typing import Dict, Any, Optional
from yookassa import Configuration, Payment

log = logging.getLogger("yookassa")

# Настройка YooKassa
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
PUBLIC_URL = os.getenv("PUBLIC_URL")

if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET_KEY
    log.info("✅ YooKassa настроена")
else:
    log.warning("⚠️ YooKassa не настроена: отсутствуют YOOKASSA_SHOP_ID или YOOKASSA_SECRET_KEY")

def create_payment(
    amount_rub: int,
    description: str,
    user_id: int,
    payment_type: str,
    plan_or_coins: str,
    return_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Создать платеж в YooKassa
    
    Args:
        amount_rub: Сумма в рублях
        description: Описание платежа
        user_id: ID пользователя
        payment_type: Тип платежа (subscription, topup)
        plan_or_coins: Название тарифа или количество монеток
        return_url: URL для возврата после оплаты
        
    Returns:
        Dict с данными платежа
    """
    try:
        if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
            return {
                "success": False,
                "error": "YooKassa не настроена"
            }
        
        # Генерируем уникальный idempotence_key
        idempotence_key = str(uuid.uuid4())
        
        # Формируем return_url
        if not return_url:
            return_url = f"{PUBLIC_URL}/payment/success"
        
        # Метаданные для webhook
        metadata = {
            "user_id": str(user_id),
            "payment_type": payment_type,
            "plan_or_coins": plan_or_coins
        }
        
        # Создаем платеж
        payment = Payment.create({
            "amount": {
                "value": f"{amount_rub}.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": metadata
        }, idempotence_key)
        
        log.info(
            f"✅ Платеж создан: id={payment.id}, amount={amount_rub}, "
            f"user={user_id}, type={payment_type}"
        )
        
        return {
            "success": True,
            "payment_id": payment.id,
            "confirmation_url": payment.confirmation.confirmation_url,
            "amount": amount_rub,
            "status": payment.status
        }
        
    except Exception as e:
        log.error(f"❌ Ошибка создания платежа: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_payment_status(payment_id: str) -> Dict[str, Any]:
    """
    Получить статус платежа
    
    Args:
        payment_id: ID платежа в YooKassa
        
    Returns:
        Dict со статусом платежа
    """
    try:
        if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
            return {
                "success": False,
                "error": "YooKassa не настроена"
            }
        
        payment = Payment.find_one(payment_id)
        
        return {
            "success": True,
            "payment_id": payment.id,
            "status": payment.status,
            "paid": payment.paid,
            "amount": float(payment.amount.value),
            "currency": payment.amount.currency,
            "metadata": payment.metadata
        }
        
    except Exception as e:
        log.error(f"❌ Ошибка получения статуса платежа {payment_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def cancel_payment(payment_id: str) -> Dict[str, Any]:
    """
    Отменить платеж
    
    Args:
        payment_id: ID платежа в YooKassa
        
    Returns:
        Dict с результатом
    """
    try:
        if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
            return {
                "success": False,
                "error": "YooKassa не настроена"
            }
        
        payment = Payment.cancel(payment_id, str(uuid.uuid4()))
        
        log.info(f"✅ Платеж отменен: {payment_id}")
        
        return {
            "success": True,
            "payment_id": payment.id,
            "status": payment.status
        }
        
    except Exception as e:
        log.error(f"❌ Ошибка отмены платежа {payment_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def create_subscription_payment(
    user_id: int,
    tariff_name: str,
    price_rub: int
) -> Dict[str, Any]:
    """
    Создать платеж для подписки
    
    Args:
        user_id: ID пользователя
        tariff_name: Название тарифа
        price_rub: Цена в рублях
        
    Returns:
        Dict с данными платежа
    """
    from app.config.pricing import get_tariff_info
    
    tariff = get_tariff_info(tariff_name)
    if not tariff:
        return {
            "success": False,
            "error": f"Тариф {tariff_name} не найден"
        }
    
    description = f"Подписка {tariff.icon} {tariff.title} на {tariff.duration_days} дней"
    
    return create_payment(
        amount_rub=price_rub,
        description=description,
        user_id=user_id,
        payment_type="subscription",
        plan_or_coins=tariff_name
    )

def create_topup_payment(
    user_id: int,
    coins: int,
    price_rub: int
) -> Dict[str, Any]:
    """
    Создать платеж для пополнения монеток
    
    Args:
        user_id: ID пользователя
        coins: Количество монеток
        price_rub: Цена в рублях
        
    Returns:
        Dict с данными платежа
    """
    description = f"Пополнение {coins} монеток"
    
    return create_payment(
        amount_rub=price_rub,
        description=description,
        user_id=user_id,
        payment_type="topup",
        plan_or_coins=str(coins)
    )

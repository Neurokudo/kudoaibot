# app/handlers/payments.py
"""Обработчики платежей и покупки тарифов"""

import logging
from aiogram import F, types
from aiogram.types import CallbackQuery

from app.services.yookassa_service import (
    create_subscription_payment,
    create_topup_payment
)
from app.config.pricing import get_tariff_info, get_topup_pack
from app.ui import Actions
from app.core.bot import dp

log = logging.getLogger("kudoaibot")

@dp.callback_query(F.data.startswith("buy_tariff_"))
async def handle_buy_tariff(callback: CallbackQuery):
    """Обработка покупки тарифа"""
    await callback.answer()
    
    tariff_name = callback.data.replace("buy_tariff_", "")
    user_id = callback.from_user.id
    
    tariff = get_tariff_info(tariff_name)
    
    if not tariff:
        await callback.message.edit_text("❌ Тариф не найден")
        return
    
    payment_result = create_subscription_payment(
        user_id=user_id,
        tariff_name=tariff_name,
        price_rub=tariff.price_rub
    )
    
    if not payment_result['success']:
        await callback.message.edit_text(
            f"❌ Ошибка создания платежа: {payment_result.get('error', 'Неизвестная ошибка')}"
        )
        return
    
    payment_text = (
        f"{tariff.icon} <b>{tariff.title}</b>\n\n"
        f"💰 Цена: {tariff.price_rub} ₽\n"
        f"💎 Монеток: {tariff.coins}\n"
        f"📅 Срок: {tariff.duration_days} дней\n\n"
        f"Для оплаты перейдите по ссылке:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💳 Оплатить", url=payment_result['confirmation_url'])],
        [types.InlineKeyboardButton(text="🏠 Главное меню", callback_data=Actions.HOME)]
    ])
    
    await callback.message.edit_text(payment_text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("buy_topup_"))
async def handle_buy_topup(callback: CallbackQuery):
    """Обработка покупки пополнения"""
    await callback.answer()
    
    coins = int(callback.data.replace("buy_topup_", ""))
    user_id = callback.from_user.id
    
    pack = get_topup_pack(coins)
    
    if not pack:
        await callback.message.edit_text("❌ Пакет не найден")
        return
    
    payment_result = create_topup_payment(
        user_id=user_id,
        coins=pack.coins,
        price_rub=pack.price_rub
    )
    
    if not payment_result['success']:
        await callback.message.edit_text(
            f"❌ Ошибка создания платежа: {payment_result.get('error', 'Неизвестная ошибка')}"
        )
        return
    
    total_coins = pack.coins + pack.bonus_coins
    payment_text = (
        f"💰 <b>Пополнение {total_coins} монеток</b>\n\n"
        f"💳 Цена: {pack.price_rub} ₽\n"
    )
    if pack.bonus_coins > 0:
        payment_text += f"🎁 Бонус: {pack.bonus_coins} монеток\n\n"
    else:
        payment_text += "\n"
    
    payment_text += "Для оплаты перейдите по ссылке:"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💳 Оплатить", url=payment_result['confirmation_url'])],
        [types.InlineKeyboardButton(text="🏠 Главное меню", callback_data=Actions.HOME)]
    ])
    
    await callback.message.edit_text(payment_text, reply_markup=keyboard)


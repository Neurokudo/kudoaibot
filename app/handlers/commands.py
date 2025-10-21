# app/handlers/commands.py
"""Обработчики команд бота (/start, /help, и т.д.)"""

import logging
from aiogram import types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.db import users
from app.services import billing
from app.ui import t
from app.ui.keyboards import build_main_menu, tariff_selection
from app.config.pricing import get_full_pricing_text
from app.core.bot import get_bot

log = logging.getLogger("kudoaibot")

def register_commands():
    """Регистрация команд"""
    bot, dp = get_bot()
    
    # Регистрируем обработчики
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_balance, Command("balance"))
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_tariffs, Command("tariffs"))

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

async def ensure_user_exists(message: Message) -> dict:
    """Убедиться, что пользователь существует в БД"""
    user = await users.get_user(message.from_user.id)
    if not user:
        user = await users.create_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language='ru'
        )
        log.info(f"✅ Создан новый пользователь: {message.from_user.id}")
    return user

async def get_user_language(user_id: int) -> str:
    """Получить язык пользователя"""
    user = await users.get_user(user_id)
    return user['language'] if user else 'ru'

async def get_user_data(user_id: int) -> dict:
    """Получить данные пользователя включая подписку"""
    user = await users.get_user(user_id)
    if not user:
        return {'subscription_type': 'Без подписки', 'videos_left': 0}
    
    status = await billing.get_user_subscription_status(user_id)
    
    return {
        'subscription_type': status.get('subscription_type', 'Без подписки'),
        'videos_left': status.get('balance', 0),
        'created_at': user.get('created_at', 'Неизвестно')
    }

# === ОБРАБОТЧИКИ КОМАНД ===

async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    user_id = message.from_user.id
    name = message.from_user.first_name or "друг"
    
    # Получаем dual balance
    from app.services.dual_balance import get_user_dual_balance, format_balance_display
    from app.services import billing
    
    balance = await get_user_dual_balance(user_id)
    
    # Получаем информацию о подписке
    status = await billing.get_user_subscription_status(user_id)
    days_left = status.get('days_left', 0) if status.get('has_active') else None
    
    welcome_text = f"👋 Привет, {name}!\n\n"
    welcome_text += f"💰 Баланс: <b>{balance_info['total']}</b> монет\n"
    welcome_text += f"🎯 Осталось: ~{balance_info['total'] // 5} видео\n\n"
    welcome_text += f"🎬 <b>Что ты можешь сделать:</b>\n"
    welcome_text += f"— Создавать видео с помощью ИИ\n"
    welcome_text += f"— Редактировать фото\n"
    welcome_text += f"— Использовать виртуальную примерочную\n\n"
    welcome_text += f"Выбери раздел ниже 👇"
    
    await message.answer(
        welcome_text,
        reply_markup=build_main_menu(user_language)
    )

async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    help_text = """
🤖 <b>KudoAiBot - Инструкция</b>

<b>РАЗДЕЛЫ:</b>

🎬 <b>ВИДЕО</b>
• SORA 2 - генерация видео через OpenAI
• VEO 3 - генерация видео через Google

<b>Режимы генерации:</b>
🤖 Умный помощник - опишите идею, GPT создаст промпт
✋ Ручной режим - введите готовый промпт
😄 Мемный режим - быстрые короткие мемы

📸 <b>ФОТО</b> (скоро)
• Различные функции для работы с фото

👗 <b>ПРИМЕРОЧНАЯ</b>
• Виртуальная примерочная одежды

💰 <b>Монетки</b>
• Генерация видео стоит монетки
• Купить можно в разделе Профиль
    """
    await message.answer(help_text)

async def cmd_balance(message: Message):
    """Показать баланс монеток"""
    await ensure_user_exists(message)
    user_id = message.from_user.id
    user_language = await get_user_language(user_id)
    
    from app.services.dual_balance import get_user_dual_balance, format_balance_display
    from app.utils.formatting import format_coins
    
    # Получаем dual balance
    balance = await get_user_dual_balance(user_id)
    status = await billing.get_user_subscription_status(user_id)
    
    balance_text = f"💰 <b>Ваш баланс</b>\n\n"
    
    # Детальный баланс
    if balance['subscription_coins'] > 0:
        balance_text += f"🟢 Подписочные: {format_coins(balance['subscription_coins'])}\n"
    if balance['permanent_coins'] > 0:
        balance_text += f"🟣 Постоянные: {format_coins(balance['permanent_coins'])}\n"
    
    balance_text += f"📊 <b>Итого: {format_coins(balance['total'])}</b>\n\n"
    
    if status['has_active']:
        balance_text += f"📋 Подписка: <b>{status['plan']}</b>\n"
        balance_text += f"🔋 Действует до: {status['expires_at'].strftime('%d.%m.%Y')}\n"
        balance_text += f"🔋 Осталось: {status['days_left']} дней\n"
    else:
        balance_text += f"📋 Подписка: <b>отсутствует</b>\n"
    
    await message.answer(balance_text)

async def cmd_profile(message: Message):
    """Показать профиль пользователя"""
    await ensure_user_exists(message)
    user_id = message.from_user.id
    
    user = await users.get_user(user_id)
    status = await billing.get_user_subscription_status(user_id)
    from app.services.dual_balance import get_user_dual_balance
    balance_info = await get_user_dual_balance(user_id)
    
    profile_text = f"👤 <b>Ваш профиль</b>\n\n"
    profile_text += f"ID: <code>{user_id}</code>\n"
    profile_text += f"Имя: {user['first_name']}\n"
    if user['username']:
        profile_text += f"Username: @{user['username']}\n"
    
    profile_text += f"\n💰 <b>Монетки</b>\n"
    profile_text += f"Баланс: <b>{status['balance']}</b>\n"
    
    if status['has_active']:
        profile_text += f"\n📋 <b>Подписка</b>\n"
        profile_text += f"План: <b>{status['plan']}</b>\n"
        profile_text += f"До: {status['expires_at'].strftime('%d.%m.%Y')}\n"
    
    await message.answer(profile_text)

async def cmd_tariffs(message: Message):
    """Показать тарифы"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    tariffs_text = get_full_pricing_text()
    await message.answer(
        tariffs_text,
        reply_markup=tariff_selection(user_language)
    )


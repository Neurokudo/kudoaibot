# app/handlers/callbacks.py
"""Обработчики callback кнопок"""

import logging
from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.db import users
from app.services import billing
from app.ui import Actions, t
from app.ui.keyboards import build_main_menu, tariff_selection, topup_packs_menu, build_profile_menu, build_tariffs_menu, build_help_menu
from app.core.bot import get_bot
from .commands import ensure_user_exists, get_user_language, get_user_data
from .video_handlers import (
    handle_video_menu,
    handle_veo3_menu,
    handle_sora2_menu,
    handle_mode_helper,
    handle_mode_manual,
    handle_mode_meme,
    handle_orientation_choice,
    handle_audio_choice,
    handle_video_regenerate,
    handle_video_to_helper
)

log = logging.getLogger("kudoaibot")

def register_callbacks():
    """Регистрация callback обработчиков"""
    bot, dp = get_bot()
    
    # Регистрируем все callback обработчики
    dp.callback_query.register(callback_home, F.data == "home")
    dp.callback_query.register(callback_video, F.data == "menu_video")
    dp.callback_query.register(callback_veo3, F.data == "video_veo3")
    dp.callback_query.register(callback_sora2, F.data == "video_sora2")
    dp.callback_query.register(callback_photo, F.data == "menu_photo")
    dp.callback_query.register(callback_tryon, F.data == "menu_tryon")
    dp.callback_query.register(callback_profile, F.data == "menu_profile")
    
    # Режимы генерации
    dp.callback_query.register(callback_mode_helper, F.data == Actions.MODE_HELPER)
    dp.callback_query.register(callback_mode_manual, F.data == Actions.MODE_MANUAL)
    dp.callback_query.register(callback_mode_meme, F.data == Actions.MODE_MEME)
    
    # Параметры видео
    dp.callback_query.register(callback_orientation_portrait, F.data == Actions.ORIENTATION_PORTRAIT)
    dp.callback_query.register(callback_orientation_landscape, F.data == Actions.ORIENTATION_LANDSCAPE)
    dp.callback_query.register(callback_audio_yes, F.data == Actions.AUDIO_YES)
    dp.callback_query.register(callback_audio_no, F.data == Actions.AUDIO_NO)
    
    # После генерации
    dp.callback_query.register(callback_video_regenerate, F.data == Actions.VIDEO_REGENERATE)
    dp.callback_query.register(callback_video_to_helper, F.data == Actions.VIDEO_TO_HELPER)
    
    # Покупка монеток
    dp.callback_query.register(callback_show_topup, F.data == "show_topup")
    
    # Тарифы
    dp.callback_query.register(callback_show_tariffs, F.data == "menu_tariffs")
    
    # Помощь
    dp.callback_query.register(callback_show_help, F.data == "menu_help")
    
    # Новые упрощенные разделы
    dp.callback_query.register(callback_show_subscriptions, F.data == "subscriptions")
    dp.callback_query.register(callback_show_permanent_coins, F.data == "permanent_coins")
    dp.callback_query.register(callback_show_coin_explanation, F.data == "coin_explanation")
    dp.callback_query.register(callback_show_models_cost, F.data == "models_cost")
    
    # Fallback для необработанных callback'ов (должен быть последним!)
    dp.callback_query.register(callback_fallback)

# === НАВИГАЦИЯ ===

async def callback_home(callback: CallbackQuery):
    """Главное меню"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    user_id = callback.from_user.id
    user_data = await get_user_data(user_id)
    name = callback.from_user.first_name or "друг"
    
    welcome_text = f"👋 {name}\n\n"
    welcome_text += f"💰 Баланс: <b>{user_data['videos_left']}</b> монет\n"
    welcome_text += f"🎬 Примерно хватит на: {user_data['videos_left'] // 5} видео\n\n"
    welcome_text += f"🎬 <b>Что ты можешь сделать:</b>\n"
    welcome_text += f"— Создавать видео с помощью ИИ\n"
    welcome_text += f"— Редактировать фото\n"
    welcome_text += f"— Использовать виртуальную примерочную\n\n"
    welcome_text += f"Выбери раздел ниже 👇"
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=build_main_menu(user_language)
    )

# === РАЗДЕЛЫ ===

async def callback_video(callback: CallbackQuery):
    """Раздел ВИДЕО"""
    await callback.answer()
    await handle_video_menu(callback)

# @dp.callback_query(F.data == Actions.VIDEO_VEO3)
async def callback_veo3(callback: CallbackQuery):
    """VEO 3 меню"""
    await callback.answer()
    await handle_veo3_menu(callback)

# @dp.callback_query(F.data == Actions.VIDEO_SORA2)
async def callback_sora2(callback: CallbackQuery):
    """SORA 2 меню"""
    await callback.answer()
    await handle_sora2_menu(callback)

# @dp.callback_query(F.data == Actions.MENU_PHOTO)
async def callback_photo(callback: CallbackQuery):
    """Раздел ФОТО"""
    await callback.answer()
    await callback.message.edit_text(
        t("menu.photo"),
        reply_markup=build_main_menu()
    )

# @dp.callback_query(F.data == Actions.MENU_TRYON)
async def callback_tryon(callback: CallbackQuery):
    """Раздел ПРИМЕРОЧНАЯ"""
    await callback.answer()
    await callback.message.edit_text(
        t("menu.tryon"),
        reply_markup=build_main_menu()
    )

# @dp.callback_query(F.data == Actions.MENU_PROFILE)
async def callback_profile(callback: CallbackQuery):
    """Профиль"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_id = callback.from_user.id
    user_language = await get_user_language(user_id)
    
    user_data = await get_user_data(user_id)
    name = callback.from_user.first_name or "Пользователь"
    
    user = await users.get_user(user_id)
    reg_date = user.get('created_at', 'Неизвестно') if user else 'Неизвестно'
    
    # Получаем детальную информацию о балансе
    from app.services.dual_balance import get_user_dual_balance
    balance_info = await get_user_dual_balance(user_id)
    
    # Рассчитываем примерное количество видео
    total_coins = balance_info['total']
    videos_left = total_coins // 5  # Примерно 5 монет за секунду видео
    
    profile_text = f"👤 <b>Мой профиль</b>\n\n"
    profile_text += f"Имя: {name}\n"
    profile_text += f"💰 Баланс: <b>{total_coins}</b> монет\n"
    
    if user_data['subscription_type'] != 'Без подписки':
        profile_text += f"📅 Подписка: {user_data['subscription_type']}\n"
    
    profile_text += f"🎬 Примерно хватит на: {videos_left} видео"
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=build_profile_menu(user_language)
    )

# === РЕЖИМЫ ГЕНЕРАЦИИ ===

# @dp.callback_query(F.data == Actions.MODE_HELPER)
async def callback_mode_helper(callback: CallbackQuery):
    """Режим умного помощника"""
    await callback.answer()
    await handle_mode_helper(callback)

# @dp.callback_query(F.data == Actions.MODE_MANUAL)
async def callback_mode_manual(callback: CallbackQuery):
    """Ручной режим"""
    await callback.answer()
    await handle_mode_manual(callback)

# @dp.callback_query(F.data == Actions.MODE_MEME)
async def callback_mode_meme(callback: CallbackQuery):
    """Мемный режим"""
    await callback.answer()
    await handle_mode_meme(callback)

# === ПАРАМЕТРЫ ВИДЕО ===

# @dp.callback_query(F.data == Actions.ORIENTATION_PORTRAIT)
async def callback_orientation_portrait(callback: CallbackQuery):
    """Портретная ориентация"""
    await callback.answer()
    await handle_orientation_choice(callback)

# @dp.callback_query(F.data == Actions.ORIENTATION_LANDSCAPE)
async def callback_orientation_landscape(callback: CallbackQuery):
    """Ландшафтная ориентация"""
    await callback.answer()
    await handle_orientation_choice(callback)

# @dp.callback_query(F.data == Actions.AUDIO_YES)
async def callback_audio_yes(callback: CallbackQuery):
    """Со звуком"""
    await callback.answer()
    await handle_audio_choice(callback)

# @dp.callback_query(F.data == Actions.AUDIO_NO)
async def callback_audio_no(callback: CallbackQuery):
    """Без звука"""
    await callback.answer()
    await handle_audio_choice(callback)

# === ПОСЛЕ ГЕНЕРАЦИИ ===

# @dp.callback_query(F.data == Actions.VIDEO_REGENERATE)
async def callback_video_regenerate(callback: CallbackQuery):
    """Повторная генерация"""
    await callback.answer()
    await handle_video_regenerate(callback)

# @dp.callback_query(F.data == Actions.VIDEO_TO_HELPER)
async def callback_video_to_helper(callback: CallbackQuery):
    """Переход к помощнику"""
    await callback.answer()
    await handle_video_to_helper(callback)

# === ПОКУПКА МОНЕТОК ===

# @dp.callback_query(F.data == Actions.PAYMENT_TOPUP)
async def callback_show_topup(callback: CallbackQuery):
    """Показать пакеты пополнения монеток"""
    await callback.answer()
    
    from app.config.pricing import format_topup_packs_text
    
    topup_text = "💰 <b>Купить монетки</b>\n\n"
    topup_text += format_topup_packs_text()
    topup_text += "\n\n💡 Выберите пакет:"
    
    await callback.message.edit_text(
        topup_text,
        reply_markup=topup_packs_menu()
    )

async def callback_show_tariffs(callback: CallbackQuery):
    """Показать меню подписки и монеток"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    tariffs_text = "💳 <b>Подписка и монетки</b>\n\n"
    tariffs_text += "Выбери, что тебе подходит:\n\n"
    tariffs_text += "🎟 <b>Подписка</b> — монетки каждый месяц на 30 дней\n"
    tariffs_text += "🟣 <b>Монетки навсегда</b> — покупаешь один раз, остаются навсегда"
    
    await callback.message.edit_text(
        tariffs_text,
        reply_markup=build_tariffs_menu(user_language)
    )

async def callback_show_help(callback: CallbackQuery):
    """Показать как это работает"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    help_text = "ℹ️ <b>Как это работает</b>\n\n"
    help_text += "Монетки — это внутренняя валюта.\n"
    help_text += "Подписка даёт монетки каждый месяц, разовые покупки — навсегда.\n"
    help_text += "Монетки тратятся на видео, фото и примерки.\n\n"
    help_text += "Всё просто: монетки = секунды или изображения."
    
    await callback.message.edit_text(
        help_text,
        reply_markup=build_help_menu(user_language)
    )

async def callback_show_subscriptions(callback: CallbackQuery):
    """Показать подписки"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    subscriptions_text = "🎟 <b>Подписка (на 30 дней)</b>\n\n"
    subscriptions_text += "Удобно, если часто создаёшь видео.\n"
    subscriptions_text += "Монетки начисляются каждый месяц и действуют 30 дней.\n\n"
    subscriptions_text += "🌱 <b>Пробный</b> — 390 ₽ → 60 монет\n"
    subscriptions_text += "✨ <b>Базовый</b> — 990 ₽ → 180 монет\n"
    subscriptions_text += "⭐ <b>Стандарт</b> — 1 990 ₽ → 400 монет\n"
    subscriptions_text += "💎 <b>Премиум</b> — 4 990 ₽ → 1 100 монет\n"
    subscriptions_text += "🔥 <b>PRO</b> — 7 490 ₽ → 1 600 монет\n\n"
    subscriptions_text += "🕐 Монетки по подписке действуют 30 дней."
    
    keyboard = [
        [btn("💰 Купить подписку", "show_plans")],
        [btn("⬅️ Назад", "menu_tariffs")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        subscriptions_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

async def callback_show_permanent_coins(callback: CallbackQuery):
    """Показать постоянные монетки"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    coins_text = "🟣 <b>Монетки навсегда</b>\n\n"
    coins_text += "Покупаешь один раз — монетки остаются навсегда.\n\n"
    coins_text += "50 монет — 990 ₽\n"
    coins_text += "130 монет — 1 990 ₽\n"
    coins_text += "280 монет — 3 990 ₽\n"
    coins_text += "575 монет — 7 490 ₽"
    
    keyboard = [
        [btn("💳 Пополнить", "show_topup")],
        [btn("⬅️ Назад", "menu_tariffs")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        coins_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

async def callback_show_models_cost(callback: CallbackQuery):
    """Показать стоимость моделей"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    cost_text = "💸 <b>Стоимость генераций:</b>\n\n"
    cost_text += "🎥 <b>Видео:</b>\n"
    cost_text += "• Veo 3 Fast — 3 мон/сек\n"
    cost_text += "• Veo 3 — 5 мон/сек\n"
    cost_text += "• Sora 2 Pro — 12 мон/сек\n"
    cost_text += "• Gemini Video — 4 мон/сек\n\n"
    cost_text += "🖼 <b>Фото:</b>\n"
    cost_text += "• Enhance / Retouch / Style — 4 монетки\n\n"
    cost_text += "👗 <b>Примерочная:</b>\n"
    cost_text += "• Imagen Try-On — 6 монет\n"
    cost_text += "• Imagen Pro — 15 монет\n\n"
    cost_text += "📘 <b>Пример:</b>\n"
    cost_text += "10 секунд Veo 3 Fast = 30 монет"
    
    keyboard = [
        [btn("⬅️ Назад", "menu_tariffs")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        cost_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# === FALLBACK ===

async def callback_fallback(callback: CallbackQuery):
    """Обработка необработанных callback'ов"""
    log.warning(f"Необработанный callback от пользователя {callback.from_user.id}: {callback.data}")
    await callback.answer("⚠️ Эта кнопка пока не работает", show_alert=True)
    
    # Показываем главное меню
    user_language = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "🏠 Главное меню",
        reply_markup=build_main_menu(user_language)
    )


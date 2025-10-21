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
    
    # Обработчики покупки
    dp.callback_query.register(callback_show_plans, F.data == "show_plans")
    dp.callback_query.register(callback_buy_tariff, F.data.startswith("buy_tariff_"))
    dp.callback_query.register(callback_buy_topup, F.data.startswith("buy_topup_"))
    
    # Обработчики фото
    dp.callback_query.register(callback_photo_enhance, F.data == "photo_enhance")
    dp.callback_query.register(callback_photo_remove_bg, F.data == "photo_remove_bg")
    dp.callback_query.register(callback_photo_retouch, F.data == "photo_retouch")
    dp.callback_query.register(callback_photo_style, F.data == "photo_style")
    
    # Обработчики примерочной
    dp.callback_query.register(callback_tryon_basic, F.data == "tryon_basic")
    dp.callback_query.register(callback_tryon_fashion, F.data == "tryon_fashion")
    dp.callback_query.register(callback_tryon_pro, F.data == "tryon_pro")
    
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
    user_language = await get_user_language(callback.from_user.id)
    
    photo_text = "🪄 <b>Редактирование фото</b>\n\n"
    photo_text += "Выберите функцию:\n\n"
    photo_text += "🪄 <b>Gemini Enhance</b> — улучшение качества\n"
    photo_text += "🪄 <b>Gemini Remove BG</b> — удаление фона\n"
    photo_text += "🪄 <b>Gemini Retouch</b> — ретушь\n"
    photo_text += "🪄 <b>Gemini Style</b> — изменение стиля\n\n"
    photo_text += "💸 <b>Стоимость:</b> 4 монетки за операцию"
    
    keyboard = [
        [btn("🪄 Enhance — 4 монетки", "photo_enhance")],
        [btn("🪄 Remove BG — 4 монетки", "photo_remove_bg")],
        [btn("🪄 Retouch — 4 монетки", "photo_retouch")],
        [btn("🪄 Style — 4 монетки", "photo_style")],
        [btn("⬅️ Назад", "home")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        photo_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# @dp.callback_query(F.data == Actions.MENU_TRYON)
async def callback_tryon(callback: CallbackQuery):
    """Раздел ПРИМЕРОЧНАЯ"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    tryon_text = "👗 <b>Виртуальная примерочная</b>\n\n"
    tryon_text += "Выберите тип примерки:\n\n"
    tryon_text += "👗 <b>Imagen Try-On</b> — базовая примерка (1 образ)\n"
    tryon_text += "👗 <b>Imagen Fashion</b> — стильная примерка\n"
    tryon_text += "👗 <b>Imagen Pro</b> — профессиональная примерка (3 образа)\n\n"
    tryon_text += "💸 <b>Стоимость:</b> от 6 до 15 монет"
    
    keyboard = [
        [btn("👗 Try-On — 6 монет", "tryon_basic")],
        [btn("👗 Fashion — 10 монет", "tryon_fashion")],
        [btn("👗 Pro — 15 монет", "tryon_pro")],
        [btn("⬅️ Назад", "home")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        tryon_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
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
        [btn("💳 50 монет — 990 ₽", "buy_topup_50")],
        [btn("💳 130 монет — 1 990 ₽", "buy_topup_130")],
        [btn("💳 280 монет — 3 990 ₽", "buy_topup_280")],
        [btn("💳 575 монет — 7 490 ₽", "buy_topup_575")],
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

async def callback_show_plans(callback: CallbackQuery):
    """Показать планы подписок для покупки"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    from app.config.pricing import TARIFFS
    
    plans_text = "💰 <b>Выберите план подписки:</b>\n\n"
    
    keyboard = []
    for key, tariff in TARIFFS.items():
        plans_text += f"{tariff.icon} <b>{tariff.title}</b> — {tariff.price_rub} ₽\n"
        plans_text += f"├ {tariff.coins} монет на {tariff.duration_days} дней\n"
        plans_text += f"└ {tariff.description}\n\n"
        
        keyboard.append([btn(f"{tariff.icon} {tariff.title} — {tariff.price_rub} ₽", f"buy_tariff_{key}")])
    
    keyboard.extend([
        [btn("⬅️ Назад", "subscriptions")],
        [btn("🏠 Главное меню", "home")]
    ])
    
    await callback.message.edit_text(
        plans_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

async def callback_buy_tariff(callback: CallbackQuery):
    """Обработка покупки тарифа"""
    await callback.answer()
    
    tariff_name = callback.data.replace("buy_tariff_", "")
    user_id = callback.from_user.id
    
    from app.config.pricing import get_tariff_info
    from app.services.yookassa_service import create_payment
    
    tariff = get_tariff_info(tariff_name)
    
    if not tariff:
        await callback.message.edit_text("❌ Тариф не найден")
        return
    
    payment_result = create_payment(
        amount_rub=tariff.price_rub,
        description=f"Подписка {tariff.title}",
        user_id=user_id,
        payment_type="subscription",
        plan_or_coins=tariff_name
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
    
    keyboard = [
        [btn("💳 Оплатить", url=payment_result['confirmation_url'])],
        [btn("⬅️ Назад", "show_plans")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        payment_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

async def callback_buy_topup(callback: CallbackQuery):
    """Обработка покупки пополнения"""
    await callback.answer()
    
    coins = int(callback.data.replace("buy_topup_", ""))
    user_id = callback.from_user.id
    
    from app.config.pricing import TOPUP_PACKS
    from app.services.yookassa_service import create_payment
    
    # Находим пакет по количеству монет
    pack = None
    for p in TOPUP_PACKS:
        if p.coins == coins:
            pack = p
            break
    
    if not pack:
        await callback.message.edit_text("❌ Пакет не найден")
        return
    
    payment_result = create_payment(
        amount_rub=pack.price_rub,
        description=f"Пополнение {pack.coins} монет",
        user_id=user_id,
        payment_type="topup",
        plan_or_coins=str(pack.coins)
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
    
    keyboard = [
        [btn("💳 Оплатить", url=payment_result['confirmation_url'])],
        [btn("⬅️ Назад", "permanent_coins")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        payment_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# === ОБРАБОТЧИКИ ФОТО ===

async def callback_photo_enhance(callback: CallbackQuery):
    """Обработка фото Enhance"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Проверяем доступ и списываем монетки
    from app.services import billing
    
    access = await billing.check_access(user_id, "photo_enhance")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 4)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    # Списываем монетки
    deduct_result = await billing.deduct_coins_for_feature(user_id, "photo_enhance")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    # Показываем информацию о списании и просим фото
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text(
        f"🪄 <b>Gemini Enhance</b>\n\n"
        f"{deduction_info}"
        f"📸 <b>Отправьте фото для улучшения качества</b>\n\n"
        f"⚠️ Поддерживаются форматы: JPG, PNG\n"
        f"📏 Максимальный размер: 10 МБ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("🏠 Главное меню", "home")]
        ])
    )

async def callback_photo_remove_bg(callback: CallbackQuery):
    """Обработка фото Remove BG"""
    await callback.answer()
    user_id = callback.from_user.id
    
    from app.services import billing
    
    access = await billing.check_access(user_id, "photo_remove_bg")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 4)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduct_result = await billing.deduct_coins_for_feature(user_id, "photo_remove_bg")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text(
        f"🪄 <b>Gemini Remove BG</b>\n\n"
        f"{deduction_info}"
        f"📸 <b>Отправьте фото для удаления фона</b>\n\n"
        f"⚠️ Поддерживаются форматы: JPG, PNG\n"
        f"📏 Максимальный размер: 10 МБ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("🏠 Главное меню", "home")]
        ])
    )

async def callback_photo_retouch(callback: CallbackQuery):
    """Обработка фото Retouch"""
    await callback.answer()
    user_id = callback.from_user.id
    
    from app.services import billing
    
    access = await billing.check_access(user_id, "photo_retouch")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 4)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduct_result = await billing.deduct_coins_for_feature(user_id, "photo_retouch")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text(
        f"🪄 <b>Gemini Retouch</b>\n\n"
        f"{deduction_info}"
        f"📸 <b>Отправьте фото для ретуши</b>\n\n"
        f"⚠️ Поддерживаются форматы: JPG, PNG\n"
        f"📏 Максимальный размер: 10 МБ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("🏠 Главное меню", "home")]
        ])
    )

async def callback_photo_style(callback: CallbackQuery):
    """Обработка фото Style"""
    await callback.answer()
    user_id = callback.from_user.id
    
    from app.services import billing
    
    access = await billing.check_access(user_id, "photo_style")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 4)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduct_result = await billing.deduct_coins_for_feature(user_id, "photo_style")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text(
        f"🪄 <b>Gemini Style</b>\n\n"
        f"{deduction_info}"
        f"📸 <b>Отправьте фото для изменения стиля</b>\n\n"
        f"⚠️ Поддерживаются форматы: JPG, PNG\n"
        f"📏 Максимальный размер: 10 МБ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("🏠 Главное меню", "home")]
        ])
    )

# === ОБРАБОТЧИКИ ПРИМЕРОЧНОЙ ===

async def callback_tryon_basic(callback: CallbackQuery):
    """Обработка примерочной Basic"""
    await callback.answer()
    user_id = callback.from_user.id
    
    from app.services import billing
    
    access = await billing.check_access(user_id, "tryon_basic")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 6)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduct_result = await billing.deduct_coins_for_feature(user_id, "tryon_basic")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text(
        f"👗 <b>Imagen Try-On</b>\n\n"
        f"{deduction_info}"
        f"📸 <b>Отправьте фото человека для примерки</b>\n\n"
        f"⚠️ Поддерживаются форматы: JPG, PNG\n"
        f"📏 Максимальный размер: 10 МБ\n"
        f"👤 Лучше всего работает с портретными фото",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("🏠 Главное меню", "home")]
        ])
    )

async def callback_tryon_fashion(callback: CallbackQuery):
    """Обработка примерочной Fashion"""
    await callback.answer()
    user_id = callback.from_user.id
    
    from app.services import billing
    
    access = await billing.check_access(user_id, "tryon_fashion")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 10)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduct_result = await billing.deduct_coins_for_feature(user_id, "tryon_fashion")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text(
        f"👗 <b>Imagen Fashion</b>\n\n"
        f"{deduction_info}"
        f"📸 <b>Отправьте фото человека для стильной примерки</b>\n\n"
        f"⚠️ Поддерживаются форматы: JPG, PNG\n"
        f"📏 Максимальный размер: 10 МБ\n"
        f"👤 Лучше всего работает с портретными фото",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("🏠 Главное меню", "home")]
        ])
    )

async def callback_tryon_pro(callback: CallbackQuery):
    """Обработка примерочной Pro"""
    await callback.answer()
    user_id = callback.from_user.id
    
    from app.services import billing
    
    access = await billing.check_access(user_id, "tryon_pro")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 15)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduct_result = await billing.deduct_coins_for_feature(user_id, "tryon_pro")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text(
        f"👗 <b>Imagen Pro</b>\n\n"
        f"{deduction_info}"
        f"📸 <b>Отправьте фото человека для профессиональной примерки</b>\n\n"
        f"⚠️ Поддерживаются форматы: JPG, PNG\n"
        f"📏 Максимальный размер: 10 МБ\n"
        f"👤 Лучше всего работает с портретными фото\n"
        f"✨ Получите 3 варианта примерки",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("🏠 Главное меню", "home")]
        ])
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


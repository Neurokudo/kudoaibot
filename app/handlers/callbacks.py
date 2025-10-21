# app/handlers/callbacks.py
"""Обработчики callback кнопок"""

import logging
from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.db import users
from app.services import billing
from app.ui import Actions, t
from app.ui.keyboards import build_main_menu, tariff_selection, topup_packs_menu, build_profile_menu, build_tariffs_menu, build_help_menu, btn
from app.core.bot import get_bot
from .commands import ensure_user_exists, get_user_language, get_user_data
from .video_handlers import (
    handle_video_menu,
    handle_orientation_choice,
    handle_audio_choice,
    handle_video_regenerate,
    handle_video_to_helper
)
from .tryon_handlers import (
    callback_tryon_start,
    callback_tryon_confirm,
    callback_tryon_swap,
    callback_tryon_reset
)

log = logging.getLogger("kudoaibot")

def register_callbacks():
    """Регистрация callback обработчиков"""
    bot, dp = get_bot()
    
    # Выбор языка
    dp.callback_query.register(callback_set_language, F.data.startswith("set_language"))
    
    # Главное меню (плоская структура)
    dp.callback_query.register(callback_home, F.data == "home")
    dp.callback_query.register(callback_create_video, F.data == "menu_create_video")
    dp.callback_query.register(callback_helper_menu, F.data == "menu_helper")
    dp.callback_query.register(callback_neurokudo_menu, F.data == "menu_neurokudo")
    dp.callback_query.register(callback_meme_menu, F.data == "menu_meme")
    dp.callback_query.register(callback_lego, F.data == "menu_lego")
    dp.callback_query.register(callback_photo, F.data == "menu_photo")
    dp.callback_query.register(callback_tryon, F.data == "menu_tryon")
    dp.callback_query.register(callback_profile, F.data == "menu_profile")
    dp.callback_query.register(callback_show_tariffs, F.data == "menu_tariffs")
    dp.callback_query.register(callback_show_help, F.data == "menu_help")
    
    # Режимы создания видео
    dp.callback_query.register(callback_video_veo3, F.data == "video_veo3")
    dp.callback_query.register(callback_video_sora2, F.data == "video_sora2")
    
    # Режимы умного помощника
    dp.callback_query.register(callback_helper_veo3, F.data == "helper_veo3")
    dp.callback_query.register(callback_helper_sora2, F.data == "helper_sora2")
    
    # Режимы Neurokudo
    dp.callback_query.register(callback_neurokudo_veo3, F.data == "neurokudo_veo3")
    dp.callback_query.register(callback_neurokudo_sora2, F.data == "neurokudo_sora2")
    
    # Режимы мемов
    dp.callback_query.register(callback_meme_veo3, F.data == "meme_veo3")
    dp.callback_query.register(callback_meme_sora2, F.data == "meme_sora2")
    
    # Обработчики покупки
    dp.callback_query.register(callback_show_plans, F.data == "show_plans")
    dp.callback_query.register(callback_buy_tariff, F.data.startswith("buy_tariff_"))
    dp.callback_query.register(callback_buy_topup, F.data.startswith("buy_topup_"))
    
    # Обработчики примерочной
    dp.callback_query.register(callback_tryon_start, F.data == "tryon_start")
    dp.callback_query.register(callback_tryon_confirm, F.data == "tryon_confirm")
    dp.callback_query.register(callback_tryon_swap, F.data == "tryon_swap")
    dp.callback_query.register(callback_tryon_reset, F.data == "tryon_reset")
    
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

async def callback_generate(callback: CallbackQuery):
    """Раздел Генерировать видео (VEO 3)"""
    await callback.answer()
    await handle_generate_menu(callback)

async def callback_lego(callback: CallbackQuery):
    """Раздел LEGO мультики"""
    await callback.answer()
    await handle_lego_menu(callback)

# @dp.callback_query(F.data == Actions.MENU_PHOTO)
async def callback_photo(callback: CallbackQuery):
    """Раздел ФОТО - временная заглушка"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    photo_text = "🪄 <b>Редактирование фото</b>\n\n"
    photo_text += "⚠️ <b>Раздел находится в разработке</b>\n\n"
    photo_text += "Скоро здесь будут доступны:\n"
    photo_text += "• Улучшение качества\n"
    photo_text += "• Удаление фона\n"
    photo_text += "• Ретушь\n"
    photo_text += "• Изменение стиля\n\n"
    photo_text += "А пока используйте 🎬 Видео и 👗 Примерочную!"
    
    keyboard = [
        [btn("⬅️ Назад", "home")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        photo_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# @dp.callback_query(F.data == Actions.MENU_TRYON)
async def callback_tryon(callback: CallbackQuery):
    """Раздел ПРИМЕРОЧНАЯ - старт"""
    await callback.answer()
    user_id = callback.from_user.id
    user_language = await get_user_language(user_id)
    
    # Инициализируем состояние примерочной
    from app.handlers.states import get_user_state, set_user_state
    state = get_user_state(user_id)
    
    # Сбрасываем предыдущее состояние примерочной
    state.tryon_data = {
        "person": None,
        "garment": None,
        "dressed": None,
        "stage": "await_person"
    }
    set_user_state(user_id, state)
    
    tryon_text = "👗 <b>Виртуальная примерочная</b>\n\n"
    tryon_text += "Давайте примерим одежду виртуально!\n\n"
    tryon_text += "📸 <b>Шаг 1:</b> Отправьте фото человека\n"
    tryon_text += "👕 <b>Шаг 2:</b> Отправьте фото одежды\n"
    tryon_text += "✨ <b>Шаг 3:</b> Получите результат!\n\n"
    tryon_text += "💸 <b>Стоимость:</b> 6 монет за примерку\n\n"
    tryon_text += "⚠️ Для лучшего результата:\n"
    tryon_text += "• Используйте портретные фото\n"
    tryon_text += "• Фото должно быть четким\n"
    tryon_text += "• Одежда на белом фоне работает лучше"
    
    keyboard = [
        [btn("📸 Начать примерку", "tryon_start")],
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
    cost_text += "• Veo 3 Pro — 5 мон/сек\n"
    cost_text += "• Sora 2 — 8 мон/сек\n"
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

async def callback_set_language(callback: CallbackQuery):
    """Обработчик выбора языка"""
    await callback.answer()
    
    # Парсим callback data
    from app.ui.callbacks import parse_cb
    cb = parse_cb(callback.data)
    language = cb.extra  # ru, en, es, ar, hi
    
    user_id = callback.from_user.id
    
    # Обновляем язык пользователя в БД
    await users.update_user_language(user_id, language)
    
    # Получаем локализованные тексты
    from app.ui.texts import t
    from app.ui.keyboards import build_main_menu
    
    # Показываем подтверждение выбора языка
    await callback.message.edit_text(
        t("language.selected", language),
        reply_markup=build_main_menu(language)
    )

# === LEGO ОБРАБОТЧИКИ ===

async def callback_lego_single(callback: CallbackQuery):
    """LEGO одна сцена"""
    await callback.answer()
    # TODO: Реализовать LEGO одну сцену
    await callback.message.edit_text(
        "🎬 <b>LEGO одна сцена</b>\n\n⚠️ Функция в разработке",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("⬅️ Назад", Actions.HOME)]
        ])
    )

async def callback_lego_reportage(callback: CallbackQuery):
    """LEGO репортаж"""
    await callback.answer()
    # TODO: Реализовать LEGO репортаж
    await callback.message.edit_text(
        "📰 <b>LEGO репортаж</b>\n\n⚠️ Функция в разработке",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("⬅️ Назад", Actions.HOME)]
        ])
    )

async def callback_lego_regenerate(callback: CallbackQuery):
    """LEGO перегенерировать"""
    await callback.answer()
    # TODO: Реализовать LEGO перегенерацию
    await callback.message.edit_text("🔄 Перегенерирую LEGO видео...")

async def callback_lego_improve(callback: CallbackQuery):
    """LEGO улучшить"""
    await callback.answer()
    # TODO: Реализовать LEGO улучшение
    await callback.message.edit_text("✨ Улучшаю LEGO видео...")

async def callback_lego_embed_replica(callback: CallbackQuery):
    """LEGO встроить реплику"""
    await callback.answer()
    # TODO: Реализовать LEGO встраивание реплики
    await callback.message.edit_text("📝 Встраиваю реплику в LEGO видео...")

# === НОВЫЕ ОБРАБОТЧИКИ ДЛЯ ПЛОСКОЙ СТРУКТУРЫ ===

async def callback_create_video(callback: CallbackQuery):
    """Обработчик меню быстрого создания видео"""
    await callback.answer()
    from app.ui.keyboards import build_create_video_menu
    from app.ui.texts import t
    
    await callback.message.edit_text(
        t("menu.create_video"),
        reply_markup=build_create_video_menu()
    )

async def callback_helper_menu(callback: CallbackQuery):
    """Обработчик меню умного помощника"""
    await callback.answer()
    from app.ui.keyboards import build_helper_menu
    from app.ui.texts import t
    
    await callback.message.edit_text(
        t("menu.helper"),
        reply_markup=build_helper_menu()
    )

async def callback_neurokudo_menu(callback: CallbackQuery):
    """Обработчик меню Neurokudo режима"""
    await callback.answer()
    from app.ui.keyboards import build_neurokudo_menu
    from app.ui.texts import t
    
    await callback.message.edit_text(
        t("menu.neurokudo"),
        reply_markup=build_neurokudo_menu()
    )

async def callback_meme_menu(callback: CallbackQuery):
    """Обработчик меню мемного режима"""
    await callback.answer()
    from app.ui.keyboards import build_meme_menu
    from app.ui.texts import t
    
    await callback.message.edit_text(
        t("menu.meme"),
        reply_markup=build_meme_menu()
    )

# === ОБРАБОТЧИКИ РЕЖИМОВ СОЗДАНИЯ ВИДЕО ===

async def callback_video_veo3(callback: CallbackQuery):
    """Быстрое создание видео VEO 3"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "manual",
        "model": "veo3",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🎬 **Быстрое создание видео VEO 3**\n\n"
        "Напишите описание сцены для генерации видео.\n"
        "Пример: \"Бабушка кормит кур во дворе\""
    )

async def callback_video_sora2(callback: CallbackQuery):
    """Быстрое создание видео SORA 2"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "manual",
        "model": "sora2",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🎬 **Быстрое создание видео SORA 2**\n\n"
        "Напишите описание сцены для генерации видео.\n"
        "Пример: \"Бабушка кормит кур во дворе\""
    )

# === ОБРАБОТЧИКИ РЕЖИМОВ УМНОГО ПОМОЩНИКА ===

async def callback_helper_veo3(callback: CallbackQuery):
    """Умный помощник VEO 3"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "helper",
        "model": "veo3",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🧠 **Умный помощник VEO 3**\n\n"
        "Напишите идею для видео. GPT улучшит ваш промпт и создаст качественное видео.\n"
        "Пример: \"Бабушка с животными\""
    )

async def callback_helper_sora2(callback: CallbackQuery):
    """Умный помощник SORA 2"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "helper",
        "model": "sora2",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🧠 **Умный помощник SORA 2**\n\n"
        "Напишите идею для видео. GPT улучшит ваш промпт и создаст качественное видео.\n"
        "Пример: \"Бабушка с животными\""
    )

# === ОБРАБОТЧИКИ РЕЖИМОВ NEUROKUDO ===

async def callback_neurokudo_veo3(callback: CallbackQuery):
    """Neurokudo режим VEO 3"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "neurokudo",
        "model": "veo3",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🔮 **Как у Neurokudo VEO 3**\n\n"
        "Специальный режим с бабушкой и абсурдными ситуациями.\n"
        "Напишите идею: \"Бабушка с динозаврами\""
    )

async def callback_neurokudo_sora2(callback: CallbackQuery):
    """Neurokudo режим SORA 2"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "neurokudo",
        "model": "sora2",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🔮 **Как у Neurokudo SORA 2**\n\n"
        "Специальный режим с бабушкой и абсурдными ситуациями.\n"
        "Напишите идею: \"Бабушка с динозаврами\""
    )

# === ОБРАБОТЧИКИ РЕЖИМОВ МЕМОВ ===

async def callback_meme_veo3(callback: CallbackQuery):
    """Мемный режим VEO 3"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "meme",
        "model": "veo3",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🤡 **Мемный режим VEO 3**\n\n"
        "Быстрая генерация смешных сцен.\n"
        "Напишите идею или нажмите кнопку для случайной сцены."
    )

async def callback_meme_sora2(callback: CallbackQuery):
    """Мемный режим SORA 2"""
    await callback.answer()
    from app.handlers.states import set_user_state
    
    user_id = callback.from_user.id
    set_user_state(user_id, {
        "mode": "meme",
        "model": "sora2",
        "awaiting_prompt": True
    })
    
    await callback.message.edit_text(
        "🤡 **Мемный режим SORA 2**\n\n"
        "Быстрая генерация смешных сцен.\n"
        "Напишите идею или нажмите кнопку для случайной сцены."
    )


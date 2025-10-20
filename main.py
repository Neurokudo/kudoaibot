"""
KudoAiBot - AI-powered Telegram bot
Разделы: ВИДЕО (SORA 2, VEO 3), ФОТО, ПРИМЕРОЧНАЯ
С умным помощником, мемным режимом и ручным режимом
"""
import os
import logging
import asyncio
import signal
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiohttp import web

# Импорты модулей бота
from app.db import database, users, subscriptions
from app.services import balance_manager, billing
from app.services.yookassa_service import (
    create_subscription_payment,
    create_topup_payment,
    get_payment_status
)
from app.config.pricing import (
    TARIFFS,
    TOPUP_PACKS,
    get_full_pricing_text,
    format_tariffs_text,
    get_feature_cost
)
from app.ui import parse_cb, Actions, t
from app.ui.keyboards import (
    build_main_menu,
    build_video_menu,
    build_veo3_modes,
    build_sora2_modes,
    tariff_selection
)
from app.handlers.states import get_user_state, is_waiting_for_input
from app.handlers.video_handlers import (
    handle_video_menu,
    handle_veo3_menu,
    handle_sora2_menu,
    handle_mode_helper,
    handle_mode_manual,
    handle_mode_meme,
    handle_text_input,
    handle_orientation_choice,
    handle_audio_choice,
    handle_video_regenerate,
    handle_video_to_helper
)

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
PORT = int(os.getenv("PORT", 8080))
TELEGRAM_MODE = os.getenv("TELEGRAM_MODE", "webhook")
DATABASE_URL = os.getenv("DATABASE_URL")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка обязательных переменных окружения
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL не найден в переменных окружения")

# Проверка опциональных переменных с предупреждениями
if not PUBLIC_URL and TELEGRAM_MODE == "webhook":
    logging.warning("⚠️ PUBLIC_URL не установлен, но используется webhook режим")

if not YOOKASSA_SECRET_KEY:
    logging.warning("⚠️ YOOKASSA_SECRET_KEY не установлен - платежи недоступны")

if not YOOKASSA_SHOP_ID:
    logging.warning("⚠️ YOOKASSA_SHOP_ID не установлен - платежи недоступны")

if not OPENAI_API_KEY:
    logging.warning("⚠️ OPENAI_API_KEY не установлен - генерация видео недоступна")

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    os.makedirs("logs", exist_ok=True)
    
    log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"
    
    handlers = [logging.StreamHandler()]
    if log_to_file:
        handlers.append(logging.FileHandler('logs/bot.log', encoding='utf-8'))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=handlers
    )
    
    log = logging.getLogger("kudoaibot")
    log.info("✅ Логирование настроено")
    return log

log = setup_logging()

# Переменные для graceful shutdown
shutdown_event = asyncio.Event()
runner = None

# Глобальные переменные для бота и диспетчера
bot = None
dp = None

def setup_bot_and_dispatcher():
    """Инициализация бота и диспетчера"""
    global bot, dp
    log.info("🔧 Инициализация бота и диспетчера...")
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    log.info("✅ Бот и диспетчер инициализированы")
    return bot, dp

bot, dp = setup_bot_and_dispatcher()

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

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    name = message.from_user.first_name or "друг"
    
    welcome_text = f"👋 Привет, {name}!\n\n"
    welcome_text += "🤖 <b>KudoAiBot</b> - твой AI помощник\n\n"
    welcome_text += "📊 Твой баланс: {videos_left} монеток\n".format(**user_data)
    welcome_text += "💼 Тариф: {subscription_type}\n\n".format(**user_data)
    welcome_text += "Выбери раздел:"
    
    await message.answer(
        welcome_text,
        reply_markup=build_main_menu(user_language)
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    help_text = """
🤖 <b>KudoAiBot - Инструкция</b>

<b>РАЗДЕЛЫ:</b>

🎬 <b>ВИДЕО</b>
• SORA 2 - генерация видео через OpenAI SORA 2
• VEO 3 - генерация видео через Google VEO 3

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

# === ОБРАБОТЧИКИ CALLBACK КНОПОК ===

@dp.callback_query(F.data == Actions.HOME)
async def callback_home(callback: CallbackQuery):
    """Главное меню"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    user_id = callback.from_user.id
    user_data = await get_user_data(user_id)
    name = callback.from_user.first_name or "друг"
    
    welcome_text = f"👋 {name}\n\n"
    welcome_text += "💰 Баланс: {videos_left} монеток\n".format(**user_data)
    welcome_text += "📊 Тариф: {subscription_type}\n\n".format(**user_data)
    welcome_text += "Выбери раздел:"
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=build_main_menu(user_language)
    )

@dp.callback_query(F.data == Actions.MENU_VIDEO)
async def callback_video(callback: CallbackQuery):
    """Раздел ВИДЕО"""
    await callback.answer()
    await handle_video_menu(callback)

@dp.callback_query(F.data == Actions.VIDEO_VEO3)
async def callback_veo3(callback: CallbackQuery):
    """VEO 3 меню"""
    await callback.answer()
    await handle_veo3_menu(callback)

@dp.callback_query(F.data == Actions.VIDEO_SORA2)
async def callback_sora2(callback: CallbackQuery):
    """SORA 2 меню"""
    await callback.answer()
    await handle_sora2_menu(callback)

@dp.callback_query(F.data == Actions.MODE_HELPER)
async def callback_mode_helper(callback: CallbackQuery):
    """Режим умного помощника"""
    await callback.answer()
    await handle_mode_helper(callback)

@dp.callback_query(F.data == Actions.MODE_MANUAL)
async def callback_mode_manual(callback: CallbackQuery):
    """Ручной режим"""
    await callback.answer()
    await handle_mode_manual(callback)

@dp.callback_query(F.data == Actions.MODE_MEME)
async def callback_mode_meme(callback: CallbackQuery):
    """Мемный режим"""
    await callback.answer()
    await handle_mode_meme(callback)

@dp.callback_query(F.data == Actions.ORIENTATION_PORTRAIT)
async def callback_orientation_portrait(callback: CallbackQuery):
    """Портретная ориентация"""
    await callback.answer()
    await handle_orientation_choice(callback)

@dp.callback_query(F.data == Actions.ORIENTATION_LANDSCAPE)
async def callback_orientation_landscape(callback: CallbackQuery):
    """Ландшафтная ориентация"""
    await callback.answer()
    await handle_orientation_choice(callback)

@dp.callback_query(F.data == Actions.AUDIO_YES)
async def callback_audio_yes(callback: CallbackQuery):
    """Со звуком"""
    await callback.answer()
    await handle_audio_choice(callback)

@dp.callback_query(F.data == Actions.AUDIO_NO)
async def callback_audio_no(callback: CallbackQuery):
    """Без звука"""
    await callback.answer()
    await handle_audio_choice(callback)

@dp.callback_query(F.data == Actions.VIDEO_REGENERATE)
async def callback_video_regenerate(callback: CallbackQuery):
    """Повторная генерация"""
    await callback.answer()
    await handle_video_regenerate(callback)

@dp.callback_query(F.data == Actions.VIDEO_TO_HELPER)
async def callback_video_to_helper(callback: CallbackQuery):
    """Переход к помощнику"""
    await callback.answer()
    await handle_video_to_helper(callback)

@dp.callback_query(F.data == Actions.MENU_PHOTO)
async def callback_photo(callback: CallbackQuery):
    """Раздел ФОТО"""
    await callback.answer()
    await callback.message.edit_text(
        t("menu.photo"),
        reply_markup=build_main_menu()
    )

@dp.callback_query(F.data == Actions.MENU_TRYON)
async def callback_tryon(callback: CallbackQuery):
    """Раздел ПРИМЕРОЧНАЯ"""
    await callback.answer()
    await callback.message.edit_text(
        t("menu.tryon"),
        reply_markup=build_main_menu()
    )

@dp.callback_query(F.data == Actions.MENU_PROFILE)
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
    
    profile_text = f"👤 <b>Профиль</b>\n\n"
    profile_text += f"Имя: {name}\n"
    profile_text += f"💰 Баланс: {user_data['videos_left']} монеток\n"
    profile_text += f"📊 Тариф: {user_data['subscription_type']}\n"
    profile_text += f"📅 Регистрация: {reg_date}\n"
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=tariff_selection(user_language)
    )

# === ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ===

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text_message(message: Message):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    
    # Проверяем, ждёт ли бот ввода от этого пользователя
    if is_waiting_for_input(user_id):
        await handle_text_input(message)
    else:
        # Если не ждём ввода, показываем меню
        await cmd_start(message)

# === ОБРАБОТЧИКИ ПОКУПКИ ТАРИФОВ ===

@dp.callback_query(F.data.startswith("buy_tariff_"))
async def handle_buy_tariff(callback: CallbackQuery):
    """Обработка покупки тарифа"""
    await callback.answer()
    
    tariff_name = callback.data.replace("buy_tariff_", "")
    user_id = callback.from_user.id
    
    from app.config.pricing import get_tariff_info
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
    
    from app.config.pricing import get_topup_pack
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

# === WEBHOOK ДЛЯ SORA 2 ===

async def sora2_callback(request):
    """Обработчик callback от OpenAI SORA 2"""
    try:
        data = await request.json()
        log.info(f"🎬 SORA 2 callback received: {data}")
        
        # Получаем данные о видео
        video_id = data.get("id")
        status = data.get("status")
        metadata = data.get("metadata", {})
        
        # Извлекаем user_id
        from app.services.clients.sora_client import extract_user_from_metadata
        user_id = extract_user_from_metadata(metadata)
        
        if status == "completed" and user_id:
            # Получаем URL видео
            video_data = data.get("output", {})
            video_url = video_data.get("url")
            
            if video_url:
                # Получаем язык пользователя
                user = await users.get_user(user_id)
                user_language = user.get('language', 'ru') if user else 'ru'
                
                # Отправляем видео пользователю
                try:
                    from app.ui.keyboards import build_video_result_menu
                    
                    await bot.send_video(
                        user_id,
                        video=video_url,
                        caption=t("video.success", cost=get_feature_cost("video_8s_audio")),
                        reply_markup=build_video_result_menu(user_language),
                        parse_mode="HTML"
                    )
                    log.info(f"✅ SORA 2 video sent to user {user_id}")
                    
                except Exception as video_error:
                    log.error(f"❌ Failed to send SORA 2 video to user {user_id}: {video_error}")
                    
                    # Fallback - отправляем ссылку
                    try:
                        await bot.send_message(
                            user_id,
                            f"✨ <b>Видео готово!</b>\n\n"
                            f"📹 <a href='{video_url}'>Смотреть видео</a>\n\n"
                            f"💰 Списано: {get_feature_cost('video_8s_audio')} монеток",
                            parse_mode="HTML"
                        )
                    except Exception as fallback_error:
                        log.error(f"❌ Fallback also failed: {fallback_error}")
            else:
                log.error(f"❌ No video URL in SORA 2 callback for user {user_id}")
        
        elif status == "failed" and user_id:
            # Обработка ошибки - возвращаем монетки
            error_data = data.get("error", {})
            error_message = error_data.get("message", "Unknown error")
            
            log.info(f"❌ SORA 2 generation failed for user {user_id}: {error_message}")
            
            # Возвращаем монетки на баланс
            try:
                # Получаем пользователя
                user = await users.get_user(user_id)
                if user:
                    current_balance = user.get('videos_left', 0)
                    # Возвращаем стоимость видео
                    cost = get_feature_cost("video_8s_audio")
                    new_balance = current_balance + cost
                    
                    # Обновляем баланс
                    await users.update_user_balance(user_id, new_balance)
                    
                    # Уведомляем пользователя
                    await bot.send_message(
                        user_id,
                        f"❌ <b>Ошибка генерации видео SORA 2</b>\n\n"
                        f"Причина: {error_message}\n\n"
                        f"💰 Монетки возвращены на баланс (+{cost})",
                        parse_mode="HTML"
                    )
                    log.info(f"✅ Refunded {cost} coins to user {user_id}")
                    
            except Exception as refund_error:
                log.error(f"❌ Error refunding coins to user {user_id}: {refund_error}")
        
        else:
            log.info(f"ℹ️ SORA 2 callback status: {status} (user_id: {user_id})")
        
        return web.Response(text="OK")
        
    except Exception as e:
        log.error(f"❌ Error in SORA 2 callback: {e}")
        import traceback
        log.error(f"❌ Traceback: {traceback.format_exc()}")
        return web.Response(text="Error", status=500)

# === WEBHOOK ДЛЯ YOOKASSA ===

async def yookassa_webhook(request):
    """Обработка webhook от YooKassa"""
    try:
        data = await request.json()
        log.info(f"📥 YooKassa webhook: {data}")
        
        event_type = data.get('event')
        payment_obj = data.get('object', {})
        
        if event_type == 'payment.succeeded':
            payment_id = payment_obj.get('id')
            metadata = payment_obj.get('metadata', {})
            
            user_id = int(metadata.get('user_id'))
            payment_type = metadata.get('payment_type')
            plan_or_coins = metadata.get('plan_or_coins')
            
            if payment_type == 'subscription':
                result = await billing.process_subscription_payment(
                    user_id=user_id,
                    tariff_name=plan_or_coins,
                    payment_id=payment_id
                )
                
                if result['success']:
                    try:
                        await bot.send_message(
                            user_id,
                            result['message']
                        )
                    except Exception as e:
                        log.error(f"Ошибка отправки уведомления: {e}")
                
            elif payment_type == 'topup':
                from app.config.pricing import get_topup_pack
                coins = int(plan_or_coins)
                pack = get_topup_pack(coins)
                
                if pack:
                    result = await billing.process_topup_payment(
                        user_id=user_id,
                        coins=pack.coins,
                        price_rub=pack.price_rub,
                        payment_id=payment_id,
                        bonus_coins=pack.bonus_coins
                    )
                    
                    if result['success']:
                        try:
                            await bot.send_message(
                                user_id,
                                result['message']
                            )
                        except Exception as e:
                            log.error(f"Ошибка отправки уведомления: {e}")
        
        return web.Response(text='OK')
        
    except Exception as e:
        log.error(f"❌ Ошибка обработки webhook: {e}")
        return web.Response(status=500)

# === КОМАНДЫ БАЛАНСА И ПРОФИЛЯ ===

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    """Показать баланс монеток"""
    await ensure_user_exists(message)
    user_id = message.from_user.id
    user_language = await get_user_language(user_id)
    
    status = await billing.get_user_subscription_status(user_id)
    balance = status['balance']
    
    balance_text = f"💰 <b>Ваш баланс</b>\n\n"
    balance_text += f"Монеток: <b>{balance}</b>\n\n"
    
    if status['has_active']:
        balance_text += f"📋 Подписка: <b>{status['plan']}</b>\n"
        balance_text += f"Действует до: {status['expires_at'].strftime('%d.%m.%Y')}\n"
        balance_text += f"Осталось дней: {status['days_left']}\n"
    else:
        balance_text += f"📋 Подписка: <b>отсутствует</b>\n"
    
    await message.answer(balance_text)

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    """Показать профиль пользователя"""
    await ensure_user_exists(message)
    user_id = message.from_user.id
    
    user = await users.get_user(user_id)
    status = await billing.get_user_subscription_status(user_id)
    summary = await balance_manager.get_user_summary(user_id, days=30)
    
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
    
    stats = summary['stats']
    if stats['spend_count'] > 0:
        profile_text += f"\n📊 <b>За 30 дней</b>\n"
        profile_text += f"Потрачено: {stats['total_spent']} монеток\n"
        profile_text += f"Операций: {stats['spend_count']}\n"
    
    await message.answer(profile_text)

@dp.message(Command("tariffs"))
async def cmd_tariffs(message: Message):
    """Показать тарифы"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    tariffs_text = get_full_pricing_text()
    await message.answer(
        tariffs_text,
        reply_markup=tariff_selection(user_language)
    )

# === ЗАПУСК БОТА ===

async def on_shutdown():
    """Действия при остановке бота"""
    log.info("🛑 Остановка бота...")
    await database.close_db()
    await bot.session.close()

async def check_expired_subscriptions_task():
    """Фоновая задача проверки истекших подписок"""
    while True:
        try:
            await asyncio.sleep(3600)  # Проверяем каждый час
            expired_count = await subscriptions.deactivate_expired_subscriptions()
            if expired_count > 0:
                log.info(f"✅ Деактивировано {expired_count} истекших подписок")
        except Exception as e:
            log.error(f"❌ Ошибка проверки подписок: {e}")

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    log.info(f"🛑 Получен сигнал {signum}, начинаем graceful shutdown...")
    shutdown_event.set()

async def graceful_shutdown():
    """Graceful shutdown функции"""
    log.info("🛑 Начинаем graceful shutdown...")
    
    if TELEGRAM_MODE == "webhook":
        try:
            await bot.delete_webhook()
            log.info("✅ Webhook удален")
        except Exception as e:
            log.error(f"❌ Ошибка удаления webhook: {e}")
    
    try:
        await bot.session.close()
        log.info("✅ Сессия бота закрыта")
    except Exception as e:
        log.error(f"❌ Ошибка закрытия сессии бота: {e}")
    
    try:
        await database.close_db()
        log.info("✅ Соединение с БД закрыто")
    except Exception as e:
        log.error(f"❌ Ошибка закрытия БД: {e}")
    
    log.info("✅ Graceful shutdown завершен")

async def setup_bot():
    """Инициализация бота и обработчиков"""
    log.info("🔧 Инициализация бота...")
    
    db_ok = await database.init_db()
    if not db_ok:
        log.error("❌ Не удалось инициализировать БД")
        raise RuntimeError("Не удалось инициализировать базу данных")
    
    log.info("✅ Подключение к базе данных установлено")
    log.info("✅ Таблицы базы данных созданы/обновлены")
    
    asyncio.create_task(check_expired_subscriptions_task())
    log.info("✅ Задача проверки подписок запущена")

async def setup_web_app(dp, bot) -> web.Application:
    """Инициализация web приложения"""
    log.info("🔧 Инициализация web приложения...")
    
    app = web.Application()
    
    async def telegram_webhook(request):
        """Обработчик Telegram webhook"""
        try:
            data = await request.json()
            update = types.Update(**data)
            await dp.feed_update(bot, update)
            return web.Response(text="OK", status=200)
        except Exception as e:
            log.exception(f"Webhook error: {e}")
            return web.Response(text="Error", status=500)
    
    app.router.add_get('/', lambda _: web.Response(text="Bot is running ✅"))
    app.router.add_post('/webhook', telegram_webhook)
    app.router.add_post('/yookassa_webhook', yookassa_webhook)
    app.router.add_post('/sora_callback', sora2_callback)  # SORA 2 callback
    
    log.info("✅ Web приложение настроено")
    return app

async def main():
    """Главная функция"""
    try:
        await setup_bot()
        
        if TELEGRAM_MODE == "webhook":
            app = await setup_web_app(dp, bot)
            
            webhook_url = f"{PUBLIC_URL}/webhook"
            await bot.set_webhook(webhook_url)
            log.info(f"✅ Webhook установлен: {webhook_url}")
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', PORT)
            await site.start()
            
            log.info(f"✅ Бот запущен в режиме webhook на порту {PORT}")
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            await shutdown_event.wait()
            
            await graceful_shutdown()
        else:
            await bot.delete_webhook()
            log.info("✅ Polling mode")
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            try:
                await dp.start_polling(bot)
            except Exception as e:
                log.error(f"❌ Ошибка polling: {e}")
            finally:
                await graceful_shutdown()
                
    except Exception as e:
        log.exception(f"Startup failed: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("🛑 Получен KeyboardInterrupt")
    except Exception as e:
        log.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

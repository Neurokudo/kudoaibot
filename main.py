"""
KudoAiBot - AI-powered Telegram bot
Объединяет Veo 3, Virtual Try-On и умную систему монеток
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
from app.services.clients import generate_video_sync, virtual_tryon
from app.config.pricing import (
    TARIFFS,
    TOPUP_PACKS,
    get_full_pricing_text,
    format_tariffs_text,
    get_feature_cost
)
from translations import get_text
from utils.keyboards import (
    main_menu,
    language_selection,
    tariff_selection
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
    # Создаем папку logs если она не существует
    os.makedirs("logs", exist_ok=True)
    
    # Проверяем, нужно ли логировать в файл
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

# Инициализируем логирование
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

# Инициализируем бота и диспетчера сразу
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
    
    # Получаем статус подписки
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
    
    # Получаем данные пользователя для приветствия
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    name = message.from_user.first_name or "друг"
    plan = user_data.get('subscription_type', 'Без подписки')
    videos_left = user_data.get('videos_left', 0)
    
    welcome_text = get_text(user_language, "welcome", 
                           name=name, 
                           plan=plan, 
                           videos_left=videos_left)
    await message.answer(
        welcome_text,
        reply_markup=main_menu(user_language)
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    help_text = get_text(user_language, "help_text")
    await message.answer(help_text)

# === ОБРАБОТЧИКИ CALLBACK КНОПОК ===

@dp.callback_query(F.data == "menu_create_video")
async def callback_menu_create_video(callback: CallbackQuery):
    """Обработчик кнопки 'Создать видео'"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    # Проверяем подписку
    user_id = callback.from_user.id
    user_data = await get_user_data(user_id)
    videos_left = user_data.get('videos_left', 0)
    
    if videos_left <= 0:
        no_videos_text = get_text(user_language, "no_videos_left")
        await callback.message.edit_text(
            no_videos_text,
            reply_markup=tariff_selection(user_language)
        )
        return
    
    # Показываем меню выбора ориентации
    orientation_text = get_text(user_language, "choose_orientation")
    from utils.keyboards import orientation_menu
    await callback.message.edit_text(
        orientation_text,
        reply_markup=orientation_menu(user_language)
    )

@dp.callback_query(F.data == "menu_examples")
async def callback_menu_examples(callback: CallbackQuery):
    """Обработчик кнопки 'Примеры'"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    examples_text = get_text(user_language, "examples")
    from utils.keyboards import video_ready_keyboard
    await callback.message.edit_text(
        examples_text,
        reply_markup=video_ready_keyboard(user_language)
    )

@dp.callback_query(F.data == "menu_profile")
async def callback_menu_profile(callback: CallbackQuery):
    """Обработчик кнопки 'Профиль'"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_id = callback.from_user.id
    user_language = await get_user_language(user_id)
    
    # Получаем данные пользователя
    user_data = await get_user_data(user_id)
    name = callback.from_user.first_name or "Пользователь"
    plan = user_data.get('subscription_type', 'Без подписки')
    videos_left = user_data.get('videos_left', 0)
    
    # Получаем дату регистрации
    user = await users.get_user(user_id)
    reg_date = user.get('created_at', 'Неизвестно') if user else 'Неизвестно'
    
    profile_text = get_text(user_language, "profile",
                           name=name,
                           plan=plan,
                           videos_left=videos_left,
                           date=reg_date)
    
    from utils.keyboards import tariff_selection
    await callback.message.edit_text(
        profile_text,
        reply_markup=tariff_selection(user_language)
    )

@dp.callback_query(F.data == "menu_help")
async def callback_menu_help(callback: CallbackQuery):
    """Обработчик кнопки 'Помощь'"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    help_text = get_text(user_language, "help_text")
    from utils.keyboards import help_keyboard
    await callback.message.edit_text(
        help_text,
        reply_markup=help_keyboard(user_language)
    )

@dp.callback_query(F.data == "menu_language")
async def callback_menu_language(callback: CallbackQuery):
    """Обработчик кнопки 'Язык'"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    language_text = get_text(user_language, "choose_language")
    from utils.keyboards import language_selection
    await callback.message.edit_text(
        language_text,
        reply_markup=language_selection()
    )

@dp.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Обработчик кнопки 'Главное меню'"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    # Получаем данные пользователя для приветствия
    user_id = callback.from_user.id
    user_data = await get_user_data(user_id)
    name = callback.from_user.first_name or "друг"
    plan = user_data.get('subscription_type', 'Без подписки')
    videos_left = user_data.get('videos_left', 0)
    
    welcome_text = get_text(user_language, "welcome", 
                           name=name, 
                           plan=plan, 
                           videos_left=videos_left)
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=main_menu(user_language)
    )

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    """Показать баланс монеток"""
    await ensure_user_exists(message)
    user_id = message.from_user.id
    user_language = await get_user_language(user_id)
    
    # Получаем статус подписки и баланс
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
    
    # Получаем данные пользователя
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
    
    # Статистика за 30 дней
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
    
    # Создаем платеж
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
    
    # Отправляем ссылку на оплату
    payment_text = (
        f"{tariff.icon} <b>{tariff.title}</b>\n\n"
        f"💰 Цена: {tariff.price_rub} ₽\n"
        f"💎 Монеток: {tariff.coins}\n"
        f"📅 Срок: {tariff.duration_days} дней\n\n"
        f"Для оплаты перейдите по ссылке:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💳 Оплатить", url=payment_result['confirmation_url'])],
        [types.InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
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
    
    # Создаем платеж
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
        [types.InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(payment_text, reply_markup=keyboard)

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
                # Обрабатываем подписку
                result = await billing.process_subscription_payment(
                    user_id=user_id,
                    tariff_name=plan_or_coins,
                    payment_id=payment_id
                )
                
                if result['success']:
                    # Уведомляем пользователя
                    try:
                        await bot.send_message(
                            user_id,
                            result['message']
                        )
                    except Exception as e:
                        log.error(f"Ошибка отправки уведомления: {e}")
                
            elif payment_type == 'topup':
                # Обрабатываем пополнение
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
                        # Уведомляем пользователя
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

# === ОБРАБОТЧИКИ VEO 3 ГЕНЕРАЦИИ ===

@dp.message(Command("generate"))
async def cmd_generate(message: Message):
    """Начать генерацию видео"""
    await ensure_user_exists(message)
    user_language = await get_user_language(message.from_user.id)
    
    await message.answer(
        "🎬 Отправьте текстовое описание видео, которое хотите создать:"
    )

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text_prompt(message: Message):
    """Обработка текстового промпта для генерации"""
    user_id = message.from_user.id
    prompt = message.text
    
    # Проверяем доступ
    access = await billing.check_access(user_id, "video_8s_mute")
    if not access['access']:
        await message.answer(access['message'])
        return
    
    # Уведомляем о начале генерации
    status_msg = await message.answer(
        "⏳ Начинаю генерацию видео...\n"
        "Это может занять 1-2 минуты."
    )
    
    try:
        # Списываем монетки
        deduct_result = await billing.deduct_coins_for_feature(user_id, "video_8s_mute")
        if not deduct_result['success']:
            await status_msg.edit_text(deduct_result['message'])
            return
        
        # Генерируем видео
        result = await asyncio.to_thread(
            generate_video_sync,
            prompt=prompt,
            duration=8,
            aspect_ratio="9:16",
            with_audio=False
        )
        
        videos = result.get('videos', [])
        if not videos:
            await status_msg.edit_text("❌ Не удалось сгенерировать видео")
            return
        
        video_file = videos[0].get('file_path')
        if video_file:
            # Отправляем видео
            with open(video_file, 'rb') as video:
                await message.answer_video(
                    video,
                    caption=f"✅ Видео готово!\n\nПромпт: {prompt[:100]}..."
                )
            
            # Удаляем статус сообщение
            await status_msg.delete()
            
            # Удаляем временный файл
            os.remove(video_file)
        else:
            await status_msg.edit_text("❌ Ошибка при получении видео")
    
    except Exception as e:
        log.error(f"Ошибка генерации видео: {e}")
        await status_msg.edit_text(f"❌ Ошибка: {str(e)}")

# === ГЛАВНОЕ МЕНЮ ===

@dp.callback_query(F.data == "main_menu")
async def handle_main_menu(callback: CallbackQuery):
    """Главное меню"""
    await callback.answer()
    user_language = await get_user_language(callback.from_user.id)
    
    welcome_text = get_text(user_language, "welcome")
    await callback.message.edit_text(
        welcome_text,
        reply_markup=main_menu(user_language)
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
    
    # Останавливаем webhook
    if TELEGRAM_MODE == "webhook":
        try:
            await bot.delete_webhook()
            log.info("✅ Webhook удален")
        except Exception as e:
            log.error(f"❌ Ошибка удаления webhook: {e}")
    
    # Закрываем соединение с ботом
    try:
        await bot.session.close()
        log.info("✅ Сессия бота закрыта")
    except Exception as e:
        log.error(f"❌ Ошибка закрытия сессии бота: {e}")
    
    # Закрываем соединение с БД
    try:
        await database.close_db()
        log.info("✅ Соединение с БД закрыто")
    except Exception as e:
        log.error(f"❌ Ошибка закрытия БД: {e}")
    
    log.info("✅ Graceful shutdown завершен")

async def setup_bot():
    """Инициализация бота и обработчиков"""
    log.info("🔧 Инициализация бота...")
    
    # Инициализация базы данных
    db_ok = await database.init_db()
    if not db_ok:
        log.error("❌ Не удалось инициализировать БД")
        raise RuntimeError("Не удалось инициализировать базу данных")
    
    log.info("✅ Подключение к базе данных установлено")
    log.info("✅ Таблицы базы данных созданы/обновлены")
    
    # Запуск задачи проверки истекших подписок
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
    
    # Health check маршрут для Railway
    app.router.add_get('/', lambda _: web.Response(text="Bot is running ✅"))
    app.router.add_post('/webhook', telegram_webhook)
    app.router.add_post('/yookassa_webhook', yookassa_webhook)
    
    log.info("✅ Web приложение настроено")
    return app

async def main():
    """Главная функция"""
    try:
        # Инициализация базы данных
        await setup_bot()
        
        if TELEGRAM_MODE == "webhook":
            # Запуск в режиме webhook
            app = await setup_web_app(dp, bot)
            
            # Установка webhook
            webhook_url = f"{PUBLIC_URL}/webhook"
            await bot.set_webhook(webhook_url)
            log.info(f"✅ Webhook установлен: {webhook_url}")
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', PORT)
            await site.start()
            
            log.info(f"✅ Бот запущен в режиме webhook на порту {PORT}")
            
            # Настраиваем обработчики сигналов
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Ждем сигнал завершения
            await shutdown_event.wait()
            
            # Graceful shutdown
            await graceful_shutdown()
        else:
            # Запуск в режиме polling
            await bot.delete_webhook()
            log.info("✅ Polling mode")
            
            # Настраиваем обработчики сигналов
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

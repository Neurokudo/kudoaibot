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
from aiohttp import web

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

# Проверка обязательных переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
PUBLIC_URL = os.getenv("PUBLIC_URL")
TELEGRAM_MODE = os.getenv("TELEGRAM_MODE", "webhook")
PORT = int(os.getenv("PORT", 8080))

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL не найден в переменных окружения")

# Проверка опциональных переменных
if not PUBLIC_URL and TELEGRAM_MODE == "webhook":
    logging.warning("⚠️ PUBLIC_URL не установлен, но используется webhook режим")

if not os.getenv("YOOKASSA_SECRET_KEY"):
    logging.warning("⚠️ YOOKASSA_SECRET_KEY не установлен - платежи недоступны")

if not os.getenv("OPENAI_API_KEY"):
    logging.warning("⚠️ OPENAI_API_KEY не установлен - SORA 2 и GPT недоступны")

if not os.getenv("GCP_KEY_JSON_B64"):
    logging.warning("⚠️ GCP_KEY_JSON_B64 не установлен - VEO 3 недоступен")

# Импорт компонентов бота
from app.core import bot, dp, setup_bot, setup_web_app, graceful_shutdown

# Регистрация обработчиков (импорт автоматически регистрирует через декораторы)
from app.handlers import commands, callbacks, payments, text

log.info("✅ Обработчики зарегистрированы")

# Переменная для graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    log.info(f"🛑 Получен сигнал {signum}, начинаем graceful shutdown...")
    shutdown_event.set()

async def main():
    """Главная функция"""
    try:
        # Инициализация бота
        await setup_bot()
        
        if TELEGRAM_MODE == "webhook":
            # Режим webhook для production
            app = await setup_web_app(dp, bot)
            
            webhook_url = f"{PUBLIC_URL}/webhook"
            await bot.set_webhook(webhook_url)
            log.info(f"✅ Webhook установлен: {webhook_url}")
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', PORT)
            await site.start()
            
            log.info(f"✅ Бот запущен в режиме webhook на порту {PORT}")
            log.info(f"🌐 PUBLIC_URL: {PUBLIC_URL}")
            
            # Настраиваем обработчики сигналов
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Ждем сигнал завершения
            await shutdown_event.wait()
            
            # Graceful shutdown
            await graceful_shutdown()
            
        else:
            # Режим polling для разработки
            await bot.delete_webhook()
            log.info("✅ Polling mode активирован")
            
            # Настраиваем обработчики сигналов
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            try:
                log.info("🚀 Запуск polling...")
                await dp.start_polling(bot)
            except Exception as e:
                log.error(f"❌ Ошибка polling: {e}")
            finally:
                await graceful_shutdown()
                
    except Exception as e:
        log.exception(f"❌ Критическая ошибка при запуске: {e}")
        raise

if __name__ == "__main__":
    try:
        log.info("=" * 50)
        log.info("🚀 KudoAiBot starting...")
        log.info(f"📊 Mode: {TELEGRAM_MODE}")
        log.info(f"🔧 Port: {PORT}")
        log.info(f"🌐 URL: {PUBLIC_URL or 'N/A (polling)'}")
        log.info("=" * 50)
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        log.info("🛑 Получен KeyboardInterrupt")
    except Exception as e:
        log.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

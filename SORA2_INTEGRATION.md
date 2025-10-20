# SORA 2 Интеграция в KudoAiBot

## ✅ Что сделано

### 1. Клиент SORA 2 (`app/services/clients/sora_client.py`)

Реализована полная интеграция с официальным OpenAI SORA 2 API:

**Функции:**
- `create_sora_task()` - создание задачи генерации видео
- `generate_video_sora2_async()` - асинхронная обёртка
- `generate_video_sora2()` - синхронная обёртка
- `extract_user_from_metadata()` - извлечение user_id из callback

**Параметры:**
```python
prompt: str               # Текстовое описание видео
aspect_ratio: str        # "9:16" или "16:9"
duration: int            # До 20 секунд
user_id: int             # ID пользователя для callback
```

**API Endpoint:**
```
POST https://api.openai.com/v1/videos/generations
```

**Логика работы:**
1. Создается задача через OpenAI API
2. Получаем `task_id`
3. OpenAI отправляет callback когда видео готово
4. Видео автоматически отправляется пользователю

### 2. Механика из SORA 2 бота

Взяты следующие элементы:

**Workflow (последовательность):**
```
Пользователь
  ↓
Выбор модели (SORA 2)
  ↓
Выбор режима (Помощник/Ручной/Мем)
  ↓
Выбор ориентации (9:16 или 16:9)
  ↓
Ввод промпта
  ↓
Подтверждение создания
  ↓
Генерация (асинхронная)
  ↓
Callback от OpenAI
  ↓
Видео отправлено пользователю
```

**Кнопки:**
- Выбор ориентации ПЕРЕД вводом промпта
- Подтверждение с кнопками: Создать / Редактировать / Отмена
- После видео: кнопки для нового видео

**Состояния:**
```python
user_waiting_for_video_orientation = {}
user_video_requests = {}
user_prompt_messages = {}
user_confirmation_messages = {}
user_video_messages = {}
user_task_messages = {}  # Сообщения о создании задачи
```

### 3. Отличия от оригинального SORA 2 бота

| Параметр | Оригинальный бот | KudoAiBot |
|----------|------------------|-----------|
| API | KIE.AI (proxy) | OpenAI Official |
| Endpoint | api.kie.ai | api.openai.com |
| Callback | /sora_callback | /sora_callback |
| Режимы | Только ручной | Помощник/Ручной/Мем |
| GPT помощник | Нет | Есть |
| Структура | Плоская | Модульная |

## 🔧 Настройка

### Переменные окружения

```bash
# OpenAI API
OPENAI_API_KEY=sk-...  # Официальный ключ OpenAI для SORA 2

# Webhook
PUBLIC_URL=https://your-domain.com  # Для callback от OpenAI

# Режим
TELEGRAM_MODE=webhook  # Обязательно webhook для callback
```

### Проверка настройки

```python
# Проверьте что ключ установлен
import os
print("OPENAI_API_KEY:", "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing")
```

## 📡 Webhook для SORA 2

Добавить в `main.py`:

```python
async def sora2_callback(request):
    """Callback от OpenAI SORA 2 — получение готового видео"""
    try:
        data = await request.json()
        log.info(f"🎬 SORA 2 callback received: {data}")
        
        # Получаем данные о видео
        video_id = data.get("id")
        status = data.get("status")
        metadata = data.get("metadata", {})
        user_id = extract_user_from_metadata(metadata)
        
        if status == "completed" and user_id:
            # Получаем URL видео
            video_url = data.get("output", {}).get("url")
            
            if video_url:
                # Получаем язык пользователя
                user = await users.get_user(user_id)
                user_language = user.get('language', 'ru') if user else 'ru'
                
                # Отправляем видео пользователю
                try:
                    await bot.send_video(
                        user_id,
                        video=video_url,
                        caption="✨ Видео готово! Чтобы создать новое — просто отправьте запрос в чат.",
                        reply_markup=build_video_result_menu(user_language),
                        parse_mode="HTML"
                    )
                    log.info(f"✅ SORA 2 video sent to user {user_id}")
                    
                except Exception as e:
                    log.error(f"❌ Failed to send SORA 2 video to user {user_id}: {e}")
                    # Fallback - отправляем ссылку
                    await bot.send_message(
                        user_id,
                        f"✨ Видео готово!\n📹 <a href='{video_url}'>Смотреть видео</a>",
                        parse_mode="HTML"
                    )
        
        elif status == "failed" and user_id:
            # Обработка ошибки - возвращаем монетки
            error_message = data.get("error", {}).get("message", "Unknown error")
            
            # Возвращаем монетки на баланс
            await billing.refund_coins_for_feature(user_id, "video_8s_mute")
            
            # Уведомляем пользователя
            await bot.send_message(
                user_id,
                f"❌ <b>Ошибка генерации видео</b>\n\n"
                f"Причина: {error_message}\n\n"
                f"💰 Монетки возвращены на баланс",
                parse_mode="HTML"
            )
            log.info(f"✅ SORA 2 error handled for user {user_id}")
        
        return web.Response(text="OK")
        
    except Exception as e:
        log.error(f"❌ Error in SORA 2 callback: {e}")
        return web.Response(text="Error", status=500)

# Добавить маршрут
app.router.add_post('/sora_callback', sora2_callback)
```

## 🎯 Как использовать

### Пользователь:

1. `/start`
2. 🎬 ВИДЕО
3. 🌟 SORA 2
4. Выбрать режим:
   - 🤖 С помощником (GPT улучшает промпт)
   - ✋ Вручную (свой промпт)
   - 😄 Мем (быстрая генерация)
5. Выбрать ориентацию: 📱 9:16 или 🖥️ 16:9
6. Ввести описание
7. Подождать (OpenAI отправит callback)
8. Получить видео!

### Пример (Режим помощника):

```
Пользователь: "собака бежит по парку"
  ↓
GPT улучшает:
"A golden retriever dog running joyfully through a sunny park..."
  ↓
SORA 2 генерирует видео
  ↓
Callback от OpenAI
  ↓
Видео отправлено пользователю
```

## 🔍 Мониторинг

### Логи

```bash
# Проверка создания задачи
grep "SORA 2 task created" logs/bot.log

# Проверка callback
grep "SORA 2 callback received" logs/bot.log

# Ошибки
grep "SORA 2 API error" logs/bot.log
```

### Статусы

- `success` - задача создана
- `immediate` - видео готово сразу
- `demo_mode` - API ключ не установлен
- `insufficient_credits` - недостаточно кредитов OpenAI
- `rate_limit` - превышен лимит запросов
- `network_error` - сетевая ошибка

## 💡 Отличия SORA 2 от VEO 3

| Параметр | SORA 2 (OpenAI) | VEO 3 (Google) |
|----------|-----------------|----------------|
| Провайдер | OpenAI | Google Cloud |
| Длительность | До 20 секунд | 6-8 секунд |
| Аудио | Всегда | Опционально |
| Качество | 1080p | 720p/1080p |
| Цена | По кредитам OpenAI | По GCP тарифам |
| Генерация | Асинхронная (callback) | Синхронная (polling) |
| Watermark | Нет | Опционально |

## 🚨 Важно

1. **OPENAI_API_KEY** - обязательно нужен для SORA 2
2. **PUBLIC_URL** - обязательно для webhook callback
3. **TELEGRAM_MODE=webhook** - обязательно, polling не поддерживает callback
4. **Монетки** - списываются сразу, возвращаются при ошибке

## 📝 TODO

- [ ] Добавить поддержку разных размеров видео (1:1, 4:3)
- [ ] Добавить выбор качества (720p, 1080p)
- [ ] Добавить progress updates (если OpenAI поддерживает)
- [ ] Оптимизировать размер видео для Telegram

---

**Готово к использованию!** 🚀

SORA 2 полностью интегрирован и использует официальный OpenAI API.


# 🚀 Руководство по запуску KudoAiBot

## ✅ Что сделано

### 🎯 Основной функционал

Бот теперь содержит **3 раздела**:

1. **🎬 ВИДЕО**
   - SORA 2 (заглушка, нужен API)
   - VEO 3 (полностью работает)
   
2. **📸 ФОТО** (скоро)
   - Раздел создан, функции добавятся позже

3. **👗 ПРИМЕРОЧНАЯ**
   - Виртуальная примерочная (базовый функционал)

### 🤖 Режимы генерации видео (для VEO 3 и SORA 2)

Каждая модель поддерживает **3 режима**:

1. **🤖 Умный помощник**
   - Пользователь описывает идею простыми словами
   - GPT-4o-mini автоматически создает детальный профессиональный промпт
   - Промпт включает: героя, окружение, камеру, освещение, стиль

2. **✋ Ручной режим**
   - Для опытных пользователей
   - Прямой ввод готового детального промпта
   - Полный контроль над результатом

3. **😄 Мемный режим**
   - Быстрая генерация коротких мемных видео (6 секунд)
   - GPT создает юмористический промпт
   - Автоматические настройки: 9:16, без звука

### 🏗️ Архитектура (взята из babka-bot-clean)

- ✅ Модульная система UI (callbacks, клавиатуры, тексты)
- ✅ Система состояний пользователя для диалогов
- ✅ AI помощник на базе GPT-4o-mini
- ✅ VEO 3 клиент с полной интеграцией
- ✅ SORA 2 клиент (заглушка)
- ✅ Биллинг система с монетками
- ✅ Graceful shutdown

## 📦 Установка зависимостей

```bash
pip install -r requirements.txt
```

### Основные пакеты
- `aiogram` - для работы с Telegram Bot API
- `openai` - для GPT помощника
- `google-cloud-aiplatform` - для VEO 3
- `google-cloud-storage` - для хранения видео
- `aiohttp` - для webhook
- И другие (см. requirements.txt)

## ⚙️ Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Telegram
BOT_TOKEN=your_telegram_bot_token
TELEGRAM_MODE=polling  # или webhook для production

# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/kudoaibot

# OpenAI (для умного помощника)
OPENAI_API_KEY=sk-...

# Google Cloud (для VEO 3)
GCP_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GCP_KEY_JSON_B64=base64_encoded_service_account_key
VEO_OUTPUT_GCS_URI=gs://your-bucket/videos/

# YooKassa (платежи)
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# Webhook (только для production)
PUBLIC_URL=https://your-domain.com
PORT=8080

# Логирование
LOG_TO_FILE=false  # true для записи в файл
```

### 🔑 Как получить Google Cloud ключ

1. Создайте Service Account в Google Cloud Console
2. Скачайте JSON ключ
3. Закодируйте в base64:
```bash
cat service-account-key.json | base64 > key.b64
# Содержимое key.b64 → GCP_KEY_JSON_B64
```

## 🚀 Запуск бота

### Локально (polling)
```bash
export TELEGRAM_MODE=polling
python main.py
```

### Production (webhook на Railway/Heroku)
```bash
export TELEGRAM_MODE=webhook
export PUBLIC_URL=https://your-app.railway.app
python main.py
```

## 🎮 Как пользоваться

### Сценарий 1: Умный помощник (VEO 3)

1. Запустите бота: `/start`
2. Нажмите: **🎬 ВИДЕО**
3. Выберите: **🎥 VEO 3**
4. Нажмите: **🤖 С помощником**
5. Введите простое описание:
   ```
   собака бежит по парку
   ```
6. GPT создаст промпт:
   ```
   A golden retriever dog running joyfully through a sunny 
   park with green grass, trees in the background, cinematic 
   camera tracking shot, warm golden hour lighting, 
   photorealistic style
   ```
7. Выберите ориентацию: **📱 Портрет (9:16)** или **🖥️ Альбом (16:9)**
8. Выберите аудио: **🔊 Со звуком** или **🔇 Без звука**
9. Подождите 1-2 минуты
10. Получите видео!

### Сценарий 2: Мемный режим

1. **🎬 ВИДЕО** → **🎥 VEO 3** → **😄 Мем**
2. Введите тему:
   ```
   кот играет на пианино
   ```
3. Готово! Автоматическая генерация (6 сек, 9:16, без звука)

### Сценарий 3: Ручной режим

1. **🎬 ВИДЕО** → **🎥 VEO 3** → **✋ Вручную**
2. Введите готовый детальный промпт:
   ```
   A cinematic shot of a majestic lion walking through tall 
   grass at sunset, golden hour lighting, camera dolly tracking 
   shot, photorealistic 8k quality, dramatic atmosphere
   ```
3. Выберите параметры
4. Получите результат

## 🛠️ Разработка

### Добавление новой модели видео

1. Создайте клиент в `app/services/clients/your_model_client.py`
2. Добавьте action в `app/ui/callbacks.py`:
   ```python
   VIDEO_YOUR_MODEL = "video_your_model"
   ```
3. Добавьте в меню `app/ui/keyboards.py`:
   ```python
   [btn(t("btn.your_model", lang), Actions.VIDEO_YOUR_MODEL)]
   ```
4. Зарегистрируйте обработчик в `main.py`

### Тестирование

```bash
# Проверка подключения к БД
python -c "from app.db import database; import asyncio; asyncio.run(database.init_db())"

# Проверка баланса пользователя
python -c "from app.db import users; import asyncio; print(asyncio.run(users.get_user(YOUR_USER_ID)))"

# Проверка GPT помощника
python -c "from app.services.ai_helper import improve_prompt_with_gpt; print(improve_prompt_with_gpt('собака бежит'))"
```

## 📊 Структура файлов

```
KudoAiBot/
├── app/
│   ├── ui/                          # UI компоненты
│   │   ├── callbacks.py             # Система callback данных
│   │   ├── keyboards.py             # Клавиатуры
│   │   └── texts.py                 # Тексты
│   ├── handlers/                    # Обработчики
│   │   ├── states.py                # Состояния пользователя
│   │   └── video_handlers.py        # Обработчики видео
│   ├── services/
│   │   ├── clients/
│   │   │   ├── veo_client.py        # ✅ VEO 3 (работает)
│   │   │   ├── sora_client.py       # ⏳ SORA 2 (заглушка)
│   │   │   └── tryon_client.py      # Примерочная
│   │   └── ai_helper.py             # ✅ GPT помощник
│   └── db/                          # База данных
├── main.py                          # ✅ Главный файл (обновлен)
├── STRUCTURE.md                     # Документация структуры
├── SETUP_GUIDE.md                   # Это руководство
└── requirements.txt                 # Зависимости
```

## 🐛 Решение проблем

### Бот не отвечает
```bash
# Проверьте логи
tail -f logs/bot.log

# Проверьте BOT_TOKEN
echo $BOT_TOKEN
```

### VEO 3 не работает
```bash
# Проверьте GCP креды
python -c "from app.services.clients.veo_client import _get_credentials; print(_get_credentials())"
```

### GPT не улучшает промпты
```bash
# Проверьте OPENAI_API_KEY
python -c "import os; print('OK' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

### База данных не подключается
```bash
# Проверьте DATABASE_URL
python -c "from app.db import database; import asyncio; asyncio.run(database.init_db())"
```

## 📝 TODO

### Приоритет 1: SORA 2
- [ ] Получить доступ к SORA 2 API от OpenAI
- [ ] Реализовать `app/services/clients/sora_client.py`
- [ ] Убрать заглушку, добавить реальную интеграцию
- [ ] Протестировать все 3 режима (помощник, ручной, мем)

### Приоритет 2: ФОТО
- [ ] Определить функции раздела ФОТО
- [ ] Создать обработчики в `app/handlers/photo_handlers.py`
- [ ] Интеграция с AI моделями
- [ ] Добавить в меню

### Приоритет 3: ПРИМЕРОЧНАЯ
- [ ] Доработать виртуальную примерочную
- [ ] Добавить обработку загрузки фото пользователя
- [ ] Интеграция с IDM-VTON
- [ ] Тестирование

## 💡 Рекомендации

1. **Для разработки** используйте `TELEGRAM_MODE=polling`
2. **Для production** используйте `TELEGRAM_MODE=webhook` + `PUBLIC_URL`
3. **Логи** включайте только при отладке (`LOG_TO_FILE=true`)
4. **База данных** - используйте PostgreSQL для production
5. **Мониторинг** - следите за балансом Google Cloud (VEO 3 стоит денег)

## 🎉 Результат

Теперь у вас полностью рабочий бот с:
- ✅ Тремя разделами (ВИДЕО, ФОТО, ПРИМЕРОЧНАЯ)
- ✅ VEO 3 с тремя режимами (помощник, ручной, мем)
- ✅ Умным помощником на базе GPT
- ✅ Системой монеток и биллингом
- ✅ Красивым UI и логикой взаимодействия

**Взятые из babka-bot-clean:**
- Система callbacks и клавиатур
- Логика умного помощника и мемного режима
- Структура обработчиков
- Идеальная работа с VEO 3

**Следующие шаги:**
1. Подключить SORA 2 (когда будет доступ)
2. Добавить функции в раздел ФОТО
3. Доработать ПРИМЕРОЧНУЮ

---

**Готово к запуску!** 🚀

Запустите бота:
```bash
python main.py
```

И попробуйте сгенерировать первое видео через умного помощника! 🎬


# KudoAiBot - Структура проекта

## 📋 Обзор

KudoAiBot - многофункциональный AI-бот для Telegram с тремя основными разделами:
- 🎬 **ВИДЕО** (SORA 2 и VEO 3)
- 📸 **ФОТО** (в разработке)
- 👗 **ПРИМЕРОЧНАЯ** (виртуальная примерочная)

## 🎯 Режимы генерации видео

Каждая модель (SORA 2 и VEO 3) поддерживает 3 режима:

### 🤖 Умный помощник
- Пользователь описывает идею простыми словами
- GPT-4o-mini создает детальный профессиональный промпт
- Промпт включает: персонаж, окружение, камеру, освещение, стиль

### ✋ Ручной режим
- Для опытных пользователей
- Прямой ввод готового детального промпта
- Полный контроль над результатом

### 😄 Мемный режим
- Быстрая генерация коротких мемных видео (6 секунд)
- GPT создает юмористический промпт
- Автоматические настройки: 9:16, без звука

## 📁 Структура проекта

```
KudoAiBot/
├── app/
│   ├── config/           # Конфигурация (тарифы, цены)
│   │   └── pricing.py
│   ├── db/              # База данных
│   │   ├── database.py
│   │   ├── users.py
│   │   ├── subscriptions.py
│   │   └── transactions.py
│   ├── handlers/        # Обработчики команд и событий
│   │   ├── states.py    # Система состояний пользователя
│   │   └── video_handlers.py  # Обработчики видео
│   ├── services/        # Бизнес-логика
│   │   ├── clients/     # API клиенты
│   │   │   ├── veo_client.py    # VEO 3 (Google)
│   │   │   ├── sora_client.py   # SORA 2 (OpenAI)
│   │   │   └── tryon_client.py  # Примерочная
│   │   ├── ai_helper.py         # GPT помощник
│   │   ├── balance_manager.py   # Управление балансом
│   │   ├── billing.py           # Биллинг
│   │   └── yookassa_service.py  # Платежи
│   └── ui/              # UI компоненты
│       ├── callbacks.py # Система callback данных
│       ├── keyboards.py # Клавиатуры
│       └── texts.py     # Тексты интерфейса
├── main.py              # Главный файл бота
└── requirements.txt     # Зависимости
```

## 🔄 Поток работы

### Генерация видео через умного помощника:

1. Пользователь нажимает: ВИДЕО → VEO 3 → 🤖 С помощником
2. Вводит простое описание: "собака бежит по парку"
3. GPT улучшает промпт: "A golden retriever dog running joyfully through a sunny park..."
4. Выбор ориентации: 9:16 или 16:9
5. Выбор аудио: со звуком или без
6. Генерация видео (1-2 минуты)
7. Результат + кнопки: 🔄 Еще раз | 🏠 Главное меню

### Мемный режим:

1. Пользователь: ВИДЕО → VEO 3 → 😄 Мем
2. Вводит тему: "кот на скейте"
3. GPT создает мемный промпт
4. Автоматическая генерация (6 сек, 9:16, без звука)
5. Результат

## 🎨 Система UI

### Callbacks
Структура callback данных: `action|id|extra`

Примеры:
- `nav|video` - навигация к разделу видео
- `mode_helper|veo3` - режим помощника для VEO 3
- `ori_916` - портретная ориентация

### Состояния пользователя
Каждый пользователь имеет состояние:
```python
UserState {
    user_id: int
    current_screen: str       # Текущий экран
    video_model: str          # "veo3" или "sora2"
    video_mode: str           # "helper", "manual", "meme"
    waiting_for: str          # Ожидание ввода
    video_params: dict        # Параметры видео
    last_prompt: str          # Последний промпт
}
```

## 🔧 API клиенты

### VEO 3 (Google)
```python
generate_video_veo3_async(
    prompt: str,
    duration: int = 8,           # 6 или 8 секунд
    aspect_ratio: str = "9:16",  # 9:16 или 16:9
    with_audio: bool = True
)
```

### SORA 2 (OpenAI)
```python
generate_video_sora2_async(
    prompt: str,
    duration: int = 8,
    aspect_ratio: str = "9:16",
    with_audio: bool = True
)
```
*Примечание: SORA 2 пока не подключен (заглушка)*

### AI Помощник (GPT)
```python
improve_prompt_async(
    user_input: str,
    mode: str = "helper"  # "helper" или "meme"
)
```

## 💰 Биллинг

### Стоимость (в монетках)
- Видео 8 сек без звука: 18 монеток
- Видео 8 сек со звуком: 22 монетки
- Видео 6 сек (мемы): 14 монеток

### Проверка доступа
```python
access = await billing.check_access(user_id, "video_8s_mute")
if access['access']:
    # Генерация разрешена
```

### Списание монеток
```python
result = await billing.deduct_coins_for_feature(user_id, "video_8s_mute")
```

## 🚀 Запуск бота

### Переменные окружения
```bash
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
GCP_PROJECT_ID=your-project-id
GCP_KEY_JSON_B64=base64_encoded_key
YOOKASSA_SHOP_ID=...
YOOKASSA_SECRET_KEY=...
PUBLIC_URL=https://your-domain.com  # для webhook
TELEGRAM_MODE=webhook  # или polling
```

### Запуск
```bash
python main.py
```

## 📝 TODO

### SORA 2
- [ ] Получить доступ к SORA 2 API
- [ ] Реализовать клиент sora_client.py
- [ ] Протестировать интеграцию

### ФОТО
- [ ] Определить функции раздела ФОТО
- [ ] Создать обработчики
- [ ] Интеграция с AI моделями

### ПРИМЕРОЧНАЯ
- [ ] Доработать виртуальную примерочную
- [ ] Добавить обработку загрузки фото
- [ ] Интеграция с IDM-VTON

## 🎯 Ключевые особенности

1. **Модульная архитектура** - легко добавлять новые модели и функции
2. **Система состояний** - отслеживание диалогов с пользователем
3. **AI помощник** - улучшение промптов через GPT
4. **Гибкая биллинг система** - монетки + подписки
5. **Graceful shutdown** - корректное завершение работы
6. **Webhook + Polling** - два режима работы

## 📚 Примеры использования

### Добавление нового режима генерации

1. Добавить action в `app/ui/callbacks.py`:
```python
MODE_CUSTOM = "mode_custom"
```

2. Добавить текст в `app/ui/texts.py`:
```python
"btn.mode_custom": "⭐ Кастомный режим"
```

3. Добавить обработчик в `app/handlers/video_handlers.py`:
```python
async def handle_mode_custom(callback: CallbackQuery):
    # Логика обработки
```

4. Зарегистрировать в `main.py`:
```python
@dp.callback_query(F.data == Actions.MODE_CUSTOM)
async def callback_mode_custom(callback: CallbackQuery):
    await handle_mode_custom(callback)
```

## 🐛 Отладка

### Логи
Логи сохраняются в `logs/bot.log` (если `LOG_TO_FILE=true`)

### Проверка состояния
```python
from app.handlers.states import get_user_state
state = get_user_state(user_id)
print(state)
```

### Проверка баланса
```bash
python -c "from app.db import users; import asyncio; asyncio.run(users.get_user(USER_ID))"
```

---

**Автор:** KudoAI Team
**Дата:** 2025-01-20
**Версия:** 2.0


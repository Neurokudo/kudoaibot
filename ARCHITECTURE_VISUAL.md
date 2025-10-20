# 🏗️ Архитектура KudoAiBot

## 📊 До и После рефакторинга

```
❌ БЫЛО:                         ✅ СТАЛО:

┌─────────────────┐              ┌─────────────────┐
│   main.py       │              │   main.py       │
│   834 строки    │              │   146 строк     │
│                 │              │                 │
│ - Импорты       │              │ - Импорты       │
│ - Настройки     │              │ - Логирование   │
│ - БД функции    │              │ - Запуск        │
│ - Команды       │              └─────────────────┘
│ - Callback'ы    │                       │
│ - Платежи       │              ┌────────┴────────┐
│ - Webhooks      │              ▼                 ▼
│ - Запуск        │         app/core/        app/handlers/
└─────────────────┘         ├── bot.py      ├── commands.py
                            └── startup.py  ├── callbacks.py
   Всё вместе!                              ├── payments.py
   Сложно читать                            ├── text.py
   Сложно менять                            └── video_handlers.py
                                                    │
                                           ┌────────┴────────┐
                                           ▼                 ▼
                                    app/webhooks/     app/services/
                                    ├── yookassa.py   └── clients/
                                    └── sora2.py          ├── sora_client.py
                                                          └── veo_client.py
   Модульно!
   Легко читать
   Легко менять
```

## 🎯 Архитектура проекта

```
KudoAiBot/
│
├── 🚀 main.py (146 строк)
│   └── Точка входа - только запуск бота
│
└── 📦 app/
    │
    ├── 🧠 core/                    - ЯДРО БОТА
    │   ├── bot.py                  - Инициализация Bot и Dispatcher
    │   └── startup.py              - Функции запуска и остановки
    │
    ├── 🎮 handlers/                - ОБРАБОТЧИКИ СОБЫТИЙ
    │   ├── commands.py             - /start, /help, /balance, /profile
    │   ├── callbacks.py            - Обработчики кнопок (меню, навигация)
    │   ├── payments.py             - Покупка тарифов и пополнение
    │   ├── text.py                 - Обработка текстовых сообщений
    │   ├── video_handlers.py       - Генерация видео (SORA 2 + VEO 3)
    │   └── states.py               - Состояния пользователя
    │
    ├── 🌐 webhooks/                - WEBHOOKS ОТ ВНЕШНИХ СЕРВИСОВ
    │   ├── yookassa.py             - Обработка платежей YooKassa
    │   └── sora2.py                - Callback от OpenAI SORA 2
    │
    ├── ⚙️ services/                - БИЗНЕС-ЛОГИКА
    │   ├── clients/                - API клиенты
    │   │   ├── veo_client.py       - Google VEO 3
    │   │   ├── sora_client.py      - OpenAI SORA 2
    │   │   └── tryon_client.py     - Виртуальная примерочная
    │   ├── ai_helper.py            - GPT помощник
    │   ├── billing.py              - Биллинг и монетки
    │   └── balance_manager.py      - Управление балансом
    │
    ├── 🎨 ui/                      - ИНТЕРФЕЙС
    │   ├── callbacks.py            - Callback система (Cb, Actions)
    │   ├── keyboards.py            - Клавиатуры
    │   └── texts.py                - Локализованные тексты
    │
    ├── 💾 db/                      - БАЗА ДАННЫХ
    │   ├── database.py             - Подключение к БД
    │   ├── users.py                - Работа с пользователями
    │   ├── subscriptions.py        - Подписки
    │   └── transactions.py         - Транзакции
    │
    └── 🔧 config/                  - КОНФИГУРАЦИЯ
        └── pricing.py              - Тарифы и цены
```

## 🔄 Поток выполнения

```
1. Пользователь отправляет /start
   ↓
2. main.py → app/handlers/commands.py
   ↓
3. commands.cmd_start()
   ↓
4. app/db/users.py → Проверка/создание пользователя
   ↓
5. app/ui/keyboards.py → Создание клавиатуры
   ↓
6. Ответ пользователю

──────────────────────────────────────

Пользователь нажимает кнопку "🎬 ВИДЕО"
   ↓
main.py → app/handlers/callbacks.py
   ↓
callbacks.callback_video() → video_handlers.handle_video_menu()
   ↓
Показ меню SORA 2 / VEO 3

──────────────────────────────────────

Пользователь выбирает SORA 2 → Умный помощник
   ↓
app/handlers/video_handlers.py
   ↓
app/services/ai_helper.py → GPT улучшает промпт
   ↓
app/services/clients/sora_client.py → Создание задачи
   ↓
OpenAI генерирует видео
   ↓
app/webhooks/sora2.py ← Callback от OpenAI
   ↓
Видео отправлено пользователю
```

## 📏 Размеры модулей

| Категория | Файл | Строк | Роль |
|-----------|------|-------|------|
| **Точка входа** | `main.py` | 146 | Запуск |
| **Ядро** | `core/bot.py` | 34 | Инициализация |
| **Ядро** | `core/startup.py` | 99 | Запуск/shutdown |
| **Обработчики** | `handlers/commands.py` | 173 | Команды |
| **Обработчики** | `handlers/callbacks.py` | 174 | Кнопки |
| **Обработчики** | `handlers/payments.py` | 103 | Платежи |
| **Обработчики** | `handlers/text.py` | 26 | Текст |
| **Обработчики** | `handlers/video_handlers.py` | 391 | Видео |
| **Обработчики** | `handlers/states.py` | 48 | Состояния |
| **Webhooks** | `webhooks/yookassa.py` | 73 | Платежи |
| **Webhooks** | `webhooks/sora2.py` | 111 | SORA 2 |

**Самый большой:** `video_handlers.py` (391 строка) - но это OK!
**Средний размер:** ~120 строк на файл ✅

## 💡 Принцип единственной ответственности

```
┌────────────────────────────────────────┐
│ Каждый модуль отвечает за ОДНО:        │
├────────────────────────────────────────┤
│ commands.py    → Команды бота          │
│ callbacks.py   → Кнопки                │
│ payments.py    → Платежи               │
│ video_handlers → Генерация видео       │
│ yookassa.py    → YooKassa webhook      │
│ sora2.py       → SORA 2 callback       │
└────────────────────────────────────────┘
```

## 🎓 Best Practices применены:

✅ **Single Responsibility** - каждый модуль одна задача
✅ **DRY (Don't Repeat Yourself)** - переиспользование кода
✅ **Separation of Concerns** - разделение ответственности
✅ **Clean Code** - читаемый, понятный код
✅ **Maintainability** - легко поддерживать

## 🚀 Как это помогает:

### Добавить новую команду?
```python
# Открываем app/handlers/commands.py (173 строки)
@dp.message(Command("new_command"))
async def cmd_new_command(message):
    # Код здесь
```

### Добавить новую кнопку?
```python
# Открываем app/handlers/callbacks.py (174 строки)
@dp.callback_query(F.data == "new_button")
async def callback_new_button(callback):
    # Код здесь
```

### Добавить новый webhook?
```python
# Создаём app/webhooks/new_service.py
async def new_service_webhook(request):
    # Код здесь
```

**Легко и понятно!** 🎯

---

## 📈 Итог:

**До:**  1 файл × 834 строки = 834 строк (монолит)
**После:** 13 файлов × ~100 строк = ~1300 строк (модульно)

Код стал немного больше (из-за импортов), но:
- ✅ В 5 раз легче читать
- ✅ В 10 раз легче поддерживать
- ✅ В 100 раз легче добавлять новое

**Это правильная архитектура для production бота!** 🏆


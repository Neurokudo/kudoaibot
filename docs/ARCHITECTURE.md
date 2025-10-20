# 🏗️ Архитектура KudoAiBot

## Общая структура

KudoAiBot построен по модульной архитектуре с четким разделением ответственности между компонентами.

## Слои приложения

```
┌─────────────────────────────────────────┐
│         Telegram Bot Layer              │
│         (aiogram, handlers)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Business Logic Layer            │
│    (billing, balance_manager)           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Service Layer                   │
│  (veo_client, tryon_client, yookassa)   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Data Layer                      │
│    (database, users, subscriptions)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         PostgreSQL Database             │
└─────────────────────────────────────────┘
```

## Компоненты

### 1. Telegram Bot Layer

**Ответственность:**
- Обработка команд и сообщений
- Управление клавиатурами
- Отправка ответов пользователям

**Файлы:**
- `main.py` - главный файл с обработчиками
- `utils/keyboards.py` - клавиатуры
- `translations.py` - переводы

### 2. Business Logic Layer

**Ответственность:**
- Бизнес-логика монеток
- Проверка доступа к функциям
- Обработка платежей
- Управление подписками

**Файлы:**
- `app/services/billing.py` - биллинг
- `app/services/balance_manager.py` - управление балансом
- `app/config/pricing.py` - конфигурация цен

### 3. Service Layer

**Ответственность:**
- Интеграция с внешними API
- Генерация контента (Veo 3, Virtual Try-On)
- Обработка платежей (YooKassa)

**Файлы:**
- `app/services/clients/veo_client.py` - Veo 3
- `app/services/clients/tryon_client.py` - Virtual Try-On
- `app/services/yookassa_service.py` - YooKassa

### 4. Data Layer

**Ответственность:**
- Работа с базой данных
- CRUD операции
- Транзакции

**Файлы:**
- `app/db/database.py` - подключение к БД
- `app/db/users.py` - операции с пользователями
- `app/db/subscriptions.py` - управление подписками
- `app/db/transactions.py` - история транзакций

## Потоки данных

### Поток создания видео

```
1. Пользователь отправляет промпт
   ↓
2. Bot Layer получает сообщение
   ↓
3. Business Logic проверяет доступ
   ↓
4. Business Logic списывает монетки
   ↓
5. Service Layer вызывает Veo 3 API
   ↓
6. Veo 3 генерирует видео
   ↓
7. Bot Layer отправляет видео пользователю
   ↓
8. Data Layer сохраняет в историю
```

### Поток оплаты подписки

```
1. Пользователь нажимает "Купить тариф"
   ↓
2. Bot Layer вызывает yookassa_service
   ↓
3. YooKassa создает платеж
   ↓
4. Bot отправляет ссылку на оплату
   ↓
5. Пользователь оплачивает
   ↓
6. YooKassa отправляет webhook
   ↓
7. Business Logic обрабатывает webhook
   ↓
8. Data Layer создает подписку
   ↓
9. Business Logic добавляет монетки
   ↓
10. Bot отправляет уведомление
```

## Безопасность

### Уровни защиты

1. **Входные данные**
   - Валидация всех параметров
   - Санитизация строк
   - Проверка типов

2. **База данных**
   - Параметризованные запросы (asyncpg)
   - Транзакции для атомарности
   - Индексы для производительности

3. **Платежи**
   - Idempotency keys
   - Проверка подписей webhook
   - Безопасное хранение ключей

4. **API**
   - Rate limiting
   - Timeout для запросов
   - Retry logic с exponential backoff

## Масштабируемость

### Горизонтальное масштабирование

**Что масштабируется:**
- ✅ Bot instances (stateless)
- ✅ Database (PostgreSQL репликация)
- ✅ Background tasks (через очереди)

**Что НЕ масштабируется:**
- ❌ Veo 3 API (лимит Google Cloud)
- ❌ YooKassa API (лимит платформы)

### Оптимизации

1. **Database Connection Pooling**
   ```python
   db_pool = await asyncpg.create_pool(
       DATABASE_URL,
       min_size=2,
       max_size=10,
       command_timeout=30
   )
   ```

2. **Async/Await везде**
   - Все IO операции асинхронны
   - Не блокируем event loop
   - Параллельные запросы

3. **Индексы БД**
   ```sql
   CREATE INDEX idx_transactions_user_id ON transactions(user_id);
   CREATE INDEX idx_subscriptions_active ON subscriptions(user_id, is_active);
   ```

## Мониторинг и логирование

### Уровни логов

```python
log.debug("Detailed info for debugging")
log.info("✅ Important events")
log.warning("⚠️ Non-critical issues")
log.error("❌ Errors that need attention")
```

### Ключевые метрики

1. **Производительность**
   - Время генерации видео
   - Время обработки платежа
   - Время ответа БД

2. **Бизнес-метрики**
   - Новые пользователи
   - Конверсия в покупку
   - Средний чек
   - LTV

3. **Технические метрики**
   - Количество запросов
   - Количество ошибок
   - Доступность API
   - Использование БД

## Тестирование

### Стратегия

1. **Unit tests**
   - Тестирование отдельных функций
   - Моки для внешних API
   - Покрытие >80%

2. **Integration tests**
   - Тестирование потоков
   - Реальная БД (тестовая)
   - Webhook симуляция

3. **End-to-end tests**
   - Сценарии пользователя
   - Реальные API (staging)
   - Автоматизация

## Деплой

### Railway (рекомендуется)

```yaml
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## Зависимости

### Критичные
- `aiogram` - Telegram bot framework
- `asyncpg` - PostgreSQL async driver
- `yookassa` - Payment processing

### Важные
- `google-cloud-storage` - Veo 3 video storage
- `Pillow` - Image processing
- `requests` - HTTP client

## Ограничения

### Текущие ограничения

1. **Veo 3**
   - Максимум 720p или 1080p
   - Только 6-8 секунд
   - Rate limit: ~100 запросов/час

2. **Virtual Try-On**
   - Только одежда (верх)
   - Требуется качественное фото
   - ~30 секунд на генерацию

3. **База данных**
   - PostgreSQL only
   - Нет шардинга
   - Вертикальное масштабирование

### Планы по устранению

- [ ] Добавить поддержку Redis для кеша
- [ ] Внедрить очереди для фоновых задач
- [ ] Добавить CDN для видео
- [ ] Оптимизировать запросы к БД

---

**Версия: 1.0**  
**Дата: 20 октября 2024**

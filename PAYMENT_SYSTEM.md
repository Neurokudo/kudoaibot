# 💰 Система оплаты KudoAiBot

## 🎯 Обзор

KudoAiBot использует **двухуровневую систему монетизации**:

1. **💎 Подписки** (тарифы на 30 дней) - даёт монетки сразу
2. **💰 Пополнение монеток** (разовые покупки) - докупка по мере необходимости

## 🏗️ Архитектура

```
Пользователь
    ↓
Профиль → Выбор (Подписка или Монетки)
    ↓
YooKassa (оплата)
    ↓
Webhook (подтверждение)
    ↓
База данных (начисление)
    ↓
Уведомление пользователю
```

## 💎 Тарифы (подписки на 30 дней)

```python
# app/config/pricing.py

TARIFFS = {
    "lite": {
        "title": "✨ Лайт",
        "price_rub": 1990,
        "coins": 250,
        "duration_days": 30
    },
    "standard": {
        "title": "⭐ Стандарт",
        "price_rub": 2990,
        "coins": 400,
        "duration_days": 30
    },
    "pro": {
        "title": "💎 Про",
        "price_rub": 4990,
        "coins": 750,
        "duration_days": 30
    }
}
```

### Что даёт подписка:

- ✅ Монетки сразу на баланс
- ✅ Монетки не сгорают после окончания подписки
- ✅ Можно накапливать монетки
- ✅ Автоматическое продление (опционально)

## 💰 Пакеты пополнения (разовая покупка)

```python
# app/config/pricing.py

TOPUP_PACKS = [
    TopupPack(coins=50,  price_rub=990,  bonus_coins=0),   # Базовый
    TopupPack(coins=120, price_rub=1990, bonus_coins=10),  # +10 бонус
    TopupPack(coins=250, price_rub=3990, bonus_coins=30),  # +30 бонус
    TopupPack(coins=500, price_rub=7490, bonus_coins=75),  # +75 бонус
]
```

### Преимущества пополнения:

- 💰 Покупаете только когда нужно
- 🎁 Бонусные монетки (от 10 до 75)
- ♾️ Монетки не сгорают никогда
- 📊 Работает без активной подписки

## 📊 Стоимость функций (в монетках)

### 🎬 Видео:

| Функция | Монетки | Описание |
|---------|---------|----------|
| VEO 3 (6 сек, без звука) | 14 | Короткое видео |
| VEO 3 (8 сек, без звука) | 18 | Стандартное видео |
| VEO 3 (8 сек, со звуком) | 26 | Видео с аудио |
| SORA 2 (5 сек) | 22 | OpenAI SORA 2 |

### 📸 Фото (скоро):

| Функция | Монетки | Описание |
|---------|---------|----------|
| Базовые операции | 1 | Простые изменения |
| Увеличение качества | 2 | Upscale |
| Улучшение фото | 3 | AI enhancement |

### 👗 Примерочная:

| Функция | Монетки | Описание |
|---------|---------|----------|
| 1 образ | 3 | Одна примерка |
| 3 образа | 8 | Три варианта |

## 🔄 Workflow покупки

### Покупка подписки:

```
1. Пользователь: /start → 👤 Профиль
   ↓
2. Бот показывает тарифы:
   ✨ Лайт — 1990 ₽ (250 монет)
   ⭐ Стандарт — 2990 ₽ (400 монет)
   💎 Про — 4990 ₽ (750 монет)
   💰 Купить монетки
   ↓
3. Пользователь выбирает тариф
   ↓
4. Бот создаёт платёж в YooKassa
   ↓
5. Пользователь оплачивает (банковская карта)
   ↓
6. YooKassa отправляет webhook → /yookassa_webhook
   ↓
7. Бот начисляет монетки на баланс
   ↓
8. Уведомление: "✅ Подписка активирована! +250 монеток"
```

### Покупка монеток:

```
1. Пользователь: Профиль → 💰 Купить монетки
   ↓
2. Бот показывает пакеты:
   💰 50 монет — 990 ₽
   💰 130 монет (120+10 бонус) — 1990 ₽
   💰 280 монет (250+30 бонус) — 3990 ₽
   💰 575 монет (500+75 бонус) — 7490 ₽
   ↓
3. Пользователь выбирает пакет
   ↓
4. Оплата через YooKassa
   ↓
5. Webhook обрабатывает платёж
   ↓
6. Монетки начислены!
```

## 🔧 Технические детали

### YooKassa интеграция

```python
# app/services/yookassa_service.py

def create_subscription_payment(user_id, tariff_name, price_rub):
    """Создать платёж для подписки"""
    payment = Payment.create({
        "amount": {"value": f"{price_rub}.00", "currency": "RUB"},
        "confirmation": {"type": "redirect"},
        "metadata": {
            "user_id": str(user_id),
            "payment_type": "subscription",
            "plan_or_coins": tariff_name
        }
    })
    return payment

def create_topup_payment(user_id, coins, price_rub):
    """Создать платёж для пополнения"""
    payment = Payment.create({
        "amount": {"value": f"{price_rub}.00", "currency": "RUB"},
        "metadata": {
            "user_id": str(user_id),
            "payment_type": "topup",
            "plan_or_coins": str(coins)
        }
    })
    return payment
```

### Webhook обработчик

```python
# app/webhooks/yookassa.py

async def yookassa_webhook(request):
    """Обработка webhook от YooKassa"""
    data = await request.json()
    
    if data['event'] == 'payment.succeeded':
        metadata = data['object']['metadata']
        user_id = int(metadata['user_id'])
        payment_type = metadata['payment_type']
        
        if payment_type == 'subscription':
            # Активировать подписку
            await billing.process_subscription_payment(...)
            
        elif payment_type == 'topup':
            # Пополнить монетки
            await billing.process_topup_payment(...)
```

## 💳 Интеграция с YooKassa

### Переменные окружения:

```bash
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
PUBLIC_URL=https://your-domain.com  # Для webhook
```

### Настройка в YooKassa:

1. Зарегистрируйтесь на https://yookassa.ru/
2. Получите `SHOP_ID` и `SECRET_KEY`
3. Настройте webhook URL: `https://your-domain.com/yookassa_webhook`
4. Добавьте в Railway переменные окружения

## 🎨 UI для покупки

### Профиль пользователя:

```
👤 Профиль

Имя: Антон
💰 Баланс: 150 монеток
📊 Тариф: ⭐ Стандарт
📅 Регистрация: 20.10.2025

┌───────────────────────────────┐
│ ✨ Лайт — 1990 ₽              │
├───────────────────────────────┤
│ ⭐ Стандарт — 2990 ₽          │
├───────────────────────────────┤
│ 💎 Про — 4990 ₽               │
├───────────────────────────────┤
│ 💰 Купить монетки             │ ← Новая кнопка!
├───────────────────────────────┤
│ 🏠 Главное меню               │
└───────────────────────────────┘
```

### Меню пополнения:

```
💰 Купить монетки

➕ Пакеты пополнения:

• 50 монет — 990 ₽
• 130 монет (120+10 бонус) — 1 990 ₽
• 280 монет (250+30 бонус) — 3 990 ₽
• 575 монет (500+75 бонус) — 7 490 ₽

💡 Монетки не сгорают и доступны без подписки!

┌───────────────────────────────┐
│ 💰 50 монет — 990 ₽           │
├───────────────────────────────┤
│ 💰 130 монет (120+10) — 1990₽│
├───────────────────────────────┤
│ 💰 280 монет (250+30) — 3990₽│
├───────────────────────────────┤
│ 💰 575 монет (500+75) — 7490₽│
├───────────────────────────────┤
│ ⬅️ К тарифам                  │
├───────────────────────────────┤
│ 🏠 Главное меню               │
└───────────────────────────────┘
```

## 💡 Примеры расчётов

### Тариф "Стандарт" (400 монеток):

```
400 монеток = 2990 ₽

Что можно сделать:
• 15 видео VEO 3 (8 сек, со звуком) по 26 монет
• или 22 видео VEO 3 (8 сек, без звука) по 18 монет
• или 133 виртуальных примерок по 3 монетки
• или 400 базовых операций с фото по 1 монетке

Цена за видео: ~199 ₽ (2990 / 15)
```

### Пакет 280 монет (250+30 бонус):

```
280 монеток = 3990 ₽

• 10 видео VEO 3 (8 сек, со звуком)
• или 15 видео VEO 3 (8 сек, без звука)
• или 93 виртуальных примерки

Цена за видео: ~399 ₽ (3990 / 10)
```

## 🔒 Безопасность

### Проверка доступа:

```python
# Перед генерацией видео
access = await billing.check_access(user_id, "video_8s_mute")

if access['access']:
    # Можно генерировать
    await generate_video(...)
else:
    # Показать сообщение о недостатке монеток
    await show_payment_options(...)
```

### Списание монеток:

```python
# Списываем только после успешного начала генерации
result = await billing.deduct_coins_for_feature(user_id, "video_8s_mute")

if result['success']:
    # Монетки списаны
    new_balance = result['new_balance']
```

### Возврат при ошибке:

```python
# Если генерация не удалась
if generation_failed:
    # Возвращаем монетки обратно
    await billing.refund_coins_for_feature(user_id, "video_8s_mute")
```

## 📱 Пользовательский опыт

### Сценарий 1: Покупка подписки

```
Пользователь: Хочу генерировать видео
    ↓
Бот: У вас 0 монеток. Купите подписку!
    ↓
Пользователь: Выбирает "⭐ Стандарт — 2990 ₽"
    ↓
Бот: Создаёт ссылку на оплату YooKassa
    ↓
Пользователь: Оплачивает картой (Visa/MasterCard/Мир)
    ↓
YooKassa: Отправляет webhook боту
    ↓
Бот: Начисляет 400 монеток
    ↓
Уведомление: "✅ Подписка активирована! +400 монеток"
    ↓
Пользователь: Может генерировать видео!
```

### Сценарий 2: Докупка монеток

```
Пользователь: Осталось 10 монеток, хочу ещё
    ↓
Бот: Профиль → 💰 Купить монетки
    ↓
Показывает пакеты с бонусами
    ↓
Пользователь: Выбирает "280 монет (250+30 бонус) — 3990 ₽"
    ↓
Оплата → Webhook → Начисление
    ↓
Уведомление: "✅ Пополнено: 250 + 30 бонус = 280 монет!"
    ↓
Баланс: 10 + 280 = 290 монеток
```

## 🎁 Бонусная система

Чем больше покупаете монеток - тем больше бонус!

```
50 монет   → 0 бонусов   (990 ₽)
120 монет  → +10 бонусов (1990 ₽)  🎁
250 монет  → +30 бонусов (3990 ₽)  🎁🎁
500 монет  → +75 бонусов (7490 ₽)  🎁🎁🎁
```

## 📊 База данных

### Таблица users:

```sql
users (
    user_id BIGINT,
    username TEXT,
    first_name TEXT,
    videos_left INT,        -- Баланс монеток
    plan_name TEXT,         -- Текущий тариф
    created_at TIMESTAMP
)
```

### Таблица subscriptions:

```sql
subscriptions (
    user_id BIGINT,
    tariff_name TEXT,
    coins INT,
    expires_at TIMESTAMP,
    is_active BOOLEAN,
    created_at TIMESTAMP
)
```

### Таблица transactions:

```sql
transactions (
    user_id BIGINT,
    amount INT,              -- Монетки (+/-)
    transaction_type TEXT,   -- spend, topup, subscription
    description TEXT,
    balance_after INT,
    created_at TIMESTAMP
)
```

## 💻 Код интеграции

### Создание платежа (подписка):

```python
# app/handlers/payments.py

@dp.callback_query(F.data.startswith("buy_tariff_"))
async def handle_buy_tariff(callback):
    tariff_name = callback.data.replace("buy_tariff_", "")
    
    # Создаём платёж
    payment = create_subscription_payment(
        user_id=user_id,
        tariff_name=tariff_name,
        price_rub=tariff.price_rub
    )
    
    # Показываем ссылку на оплату
    await callback.message.edit_text(
        f"💳 Оплатить: {payment['confirmation_url']}"
    )
```

### Создание платежа (монетки):

```python
@dp.callback_query(F.data.startswith("buy_topup_"))
async def handle_buy_topup(callback):
    coins = int(callback.data.replace("buy_topup_", ""))
    
    pack = get_topup_pack(coins)
    
    payment = create_topup_payment(
        user_id=user_id,
        coins=pack.coins,
        price_rub=pack.price_rub
    )
    
    await show_payment_link(payment)
```

### Обработка webhook:

```python
# app/webhooks/yookassa.py

async def yookassa_webhook(request):
    data = await request.json()
    
    if data['event'] == 'payment.succeeded':
        metadata = data['object']['metadata']
        
        if metadata['payment_type'] == 'subscription':
            # Активировать подписку
            await billing.process_subscription_payment(
                user_id, tariff_name, payment_id
            )
            
        elif metadata['payment_type'] == 'topup':
            # Пополнить монетки
            await billing.process_topup_payment(
                user_id, coins, price_rub, bonus_coins
            )
```

## 📈 Аналитика

### Метрики для отслеживания:

```python
# Ежедневная статистика
- Новые подписки: COUNT(subscriptions WHERE date = today)
- Пополнения: COUNT(transactions WHERE type = 'topup')
- Выручка: SUM(amount) WHERE date = today

# Пользовательская активность
- Активные подписки: COUNT(subscriptions WHERE is_active = true)
- Средний баланс: AVG(users.videos_left)
- Конверсия: подписок / новых пользователей
```

## 🎯 Стратегия монетизации

### Почему две системы?

1. **Подписки (тарифы)**
   - ✅ Предсказуемый доход
   - ✅ Долгосрочные клиенты
   - ✅ Более выгодно для пользователя (больше монеток)

2. **Пополнения (монетки)**
   - ✅ Низкий порог входа
   - ✅ Гибкость для пользователя
   - ✅ Дополнительный доход от активных пользователей

### Pricing стратегия:

```
Подписка "Стандарт": 400 монет = 2990 ₽ → 7.47 ₽/монетка
Пакет 250 монет: 280 монет = 3990 ₽ → 14.25 ₽/монетка

Подписка выгоднее почти в 2 раза!
→ Мотивация покупать подписку
```

## 📝 TODO

- [ ] Добавить автопродление подписки
- [ ] Добавить промокоды
- [ ] Добавить реферальную программу
- [ ] Добавить специальные акции (Black Friday и т.д.)
- [ ] Интеграция с другими платёжными системами (Stripe для международных)

## ✅ Что уже работает

✅ Тарифы на 30 дней (3 уровня)
✅ Пакеты пополнения (4 пакета с бонусами)
✅ YooKassa интеграция
✅ Webhook обработка
✅ Начисление монеток
✅ Списание монеток за функции
✅ Возврат монеток при ошибках
✅ История транзакций
✅ Проверка баланса перед операцией

---

**Система оплаты полностью готова и работает!** 💰


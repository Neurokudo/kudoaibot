# ✅ Чек-лист деплоя KudoAiBot

## 📋 Перед началом

```
[ ] У меня есть аккаунт GitHub
[ ] У меня есть аккаунт Railway (или готов создать)
[ ] Установлен Git на компьютере
[ ] Есть токен от @BotFather
```

---

## 🔑 API Ключи для сбора

### 1. Telegram Bot Token
```
Где получить: @BotFather в Telegram
Команда: /newbot
Формат: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

✅ Получил: _______________________________________________
```

### 2. YooKassa (для платежей)
```
Где получить: yookassa.ru → Личный кабинет → Интеграция
Регистрация: ~1-2 дня модерации

Shop ID:     ✅ _______________________________________________
Secret Key:  ✅ _______________________________________________
```

### 3. Google Cloud Platform
```
Где получить: console.cloud.google.com
Нужно:
- Создать проект
- Включить Vertex AI API
- Создать Service Account
- Скачать JSON ключ
- Конвертировать в Base64

Project ID:  ✅ _______________________________________________
Key Base64:  ✅ (длинная строка ~2000+ символов)
```

---

## 🚀 Шаги деплоя

### ШАГ 1: GitHub (5 минут)

```bash
cd ~/Desktop/KudoAiBot

# 1. Инициализируйте Git
[ ] git init

# 2. Добавьте файлы
[ ] git add .
[ ] git commit -m "Initial commit"

# 3. Создайте репозиторий на GitHub.com
[ ] Зашел на github.com
[ ] Нажал "New repository"
[ ] Назвал "KudoAiBot"
[ ] Выбрал Private
[ ] НЕ добавлял README (уже есть)
[ ] Создал репозиторий

# 4. Подключите и залейте
[ ] git remote add origin https://github.com/USERNAME/KudoAiBot.git
[ ] git branch -M main
[ ] git push -u origin main
```

**Результат:** ✅ Код на GitHub

---

### ШАГ 2: Railway - Создание проекта (3 минуты)

```
1. [ ] Зашел на railway.app
2. [ ] Login with GitHub
3. [ ] New Project
4. [ ] Deploy from GitHub repo
5. [ ] Выбрал KudoAiBot
6. [ ] Deploy Now
```

**Результат:** ✅ Проект создан

---

### ШАГ 3: Railway - Добавить PostgreSQL (1 минута)

```
1. [ ] В проекте нажал "+ New"
2. [ ] Выбрал "Database"
3. [ ] Выбрал "Add PostgreSQL"
```

**Результат:** ✅ База данных создана

---

### ШАГ 4: Railway - Переменные окружения (10 минут)

Откройте сервис KudoAiBot → Variables → + New Variable

**Обязательные (без них не запустится):**

```
[ ] BOT_TOKEN = (от @BotFather)
[ ] DATABASE_URL = (автоматически из PostgreSQL)
[ ] PUBLIC_URL = (будет после деплоя, заполните потом)
[ ] TELEGRAM_MODE = webhook
[ ] PORT = 8080
```

**Для платежей (YooKassa):**

```
[ ] YOOKASSA_SHOP_ID = (ваш shop id)
[ ] YOOKASSA_SECRET_KEY = (ваш secret key)
```

**Для AI функций (Google Cloud):**

```
[ ] GCP_PROJECT_ID = (ваш project id)
[ ] GCP_KEY_JSON_B64 = (base64 строка)
[ ] GOOGLE_CLOUD_LOCATION = us-central1
[ ] VEO_MODEL = veo-3.0-fast-generate-001
```

**Дополнительные:**

```
[ ] HTTP_TIMEOUT = 60
[ ] HTTP_RETRIES = 3
[ ] TRYON_HTTP_TIMEOUT = 240
[ ] DOWNLOAD_VIDEOS = 1
```

**Результат:** ✅ Все переменные добавлены

---

### ШАГ 5: Railway - Получить PUBLIC_URL (2 минуты)

```
1. [ ] Подождал пока бот задеплоится (1-2 мин)
2. [ ] Открыл Settings → Networking
3. [ ] Нажал "Generate Domain"
4. [ ] Скопировал URL (например: kudoaibot-production.up.railway.app)
5. [ ] Добавил в Variables:
      PUBLIC_URL = https://kudoaibot-production.up.railway.app
```

**Результат:** ✅ PUBLIC_URL настроен

---

### ШАГ 6: Telegram - Настроить webhook (2 минуты)

```
1. [ ] Открыл Telegram, нашел @BotFather
2. [ ] Отправил /setwebhook
3. [ ] Выбрал своего бота
4. [ ] Вставил URL:
      https://kudoaibot-production.up.railway.app/webhook
```

**Результат:** ✅ Webhook настроен

---

### ШАГ 7: YooKassa - Настроить webhook (2 минуты)

```
1. [ ] Зашел на yookassa.ru
2. [ ] Личный кабинет → Интеграция
3. [ ] HTTP-уведомления → Добавить
4. [ ] URL: https://kudoaibot-production.up.railway.app/yookassa_webhook
5. [ ] События: payment.succeeded, payment.canceled
6. [ ] Сохранил
```

**Результат:** ✅ YooKassa webhook настроен

---

### ШАГ 8: Проверка (5 минут)

**Railway логи:**
```
[ ] Открыл Deployments → View Logs
[ ] Увидел: "✅ Подключение к базе данных установлено"
[ ] Увидел: "✅ Таблицы базы данных созданы"
[ ] Увидел: "✅ Webhook установлен"
[ ] Увидел: "✅ Бот запущен в режиме webhook"
```

**Telegram бот:**
```
[ ] Нашел бота в Telegram
[ ] Отправил /start
[ ] Получил приветствие
[ ] Отправил /balance
[ ] Увидел баланс (0 монеток)
[ ] Отправил /tariffs
[ ] Увидел список тарифов
```

**База данных:**
```
[ ] Railway → PostgreSQL → Data
[ ] Увидел таблицы: users, subscriptions, transactions, payments, generations
```

**Результат:** ✅ Всё работает!

---

## 🎉 ГОТОВО!

```
✅ Код на GitHub
✅ Бот задеплоен на Railway
✅ База данных работает
✅ Webhook настроены
✅ Бот отвечает в Telegram
```

---

## 📊 Что дальше?

### Тестирование платежей (YooKassa)

```
1. [ ] Создал тестовый платеж
2. [ ] Проверил что монетки зачисляются
3. [ ] Проверил что webhook приходит
```

### Тестирование AI функций

```
1. [ ] Попробовал сгенерировать видео (Veo 3)
2. [ ] Попробовал Virtual Try-On
3. [ ] Проверил что монетки списываются
```

### Мониторинг

```
1. [ ] Добавил в закладки Railway Dashboard
2. [ ] Проверяю логи раз в день
3. [ ] Мониторю использование кредитов
```

---

## 🆘 Если что-то не работает

### Бот не отвечает?
```
1. Проверьте логи в Railway
2. Проверьте PUBLIC_URL в переменных
3. Проверьте webhook в @BotFather: /setwebhook
```

### База данных не подключается?
```
1. Railway → PostgreSQL → Connect
2. Скопируйте новый DATABASE_URL
3. Обновите переменную в сервисе
```

### Платежи не работают?
```
1. Проверьте YOOKASSA_* переменные
2. Проверьте webhook в личном кабинете YooKassa
3. Проверьте логи Railway (ошибки?)
```

### Veo 3 не генерирует?
```
1. Проверьте GCP_KEY_JSON_B64
2. Google Cloud Console → API включен?
3. Проверьте квоты в GCP
```

---

## 💡 Полезные команды

### Проверить webhook Telegram
```bash
curl https://api.telegram.org/bot<ВАШ_TOKEN>/getWebhookInfo
```

### Проверить подключение к БД
```bash
# В Railway → PostgreSQL → Connect → получите URL
psql "postgresql://..." -c "SELECT COUNT(*) FROM users"
```

### Обновить код
```bash
cd ~/Desktop/KudoAiBot
git add .
git commit -m "Обновление"
git push origin main
# Railway автоматически задеплоит!
```

---

## 📞 Поддержка

- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app
- Полная инструкция: DEPLOY_GUIDE.md

---

**Время на деплой: ~30 минут**  
**Сложность: Средняя**  
**Стоимость: $5-10/месяц**

🎊 Удачи!

# ⚡ Быстрый старт KudoAiBot

## 🎯 За 5 минут до запуска!

### Шаг 1: Создайте бота в Telegram
```
1. Откройте @BotFather в Telegram
2. Отправьте /newbot
3. Введите название: KudoAiBot
4. Введите username: kudoai_bot
5. Получите токен: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Шаг 2: Создайте базу данных PostgreSQL

**Вариант A: Railway (рекомендуется)**
```
1. Зайдите на railway.app
2. Нажмите "New Project" → "Provision PostgreSQL"
3. Скопируйте DATABASE_URL из Variables
```

**Вариант B: Локально**
```bash
# macOS
brew install postgresql
brew services start postgresql
createdb kudoaibot

# DATABASE_URL будет:
# postgresql://username@localhost:5432/kudoaibot
```

### Шаг 3: Настройте YooKassa

```
1. Зайдите на yookassa.ru
2. Зарегистрируйте магазин
3. Получите Shop ID и Secret Key
4. Добавьте webhook: https://ваш-домен.com/yookassa_webhook
```

### Шаг 4: Настройте Google Cloud (для Veo 3)

```
1. Зайдите на console.cloud.google.com
2. Создайте проект
3. Включите Vertex AI API
4. Создайте Service Account
5. Скачайте JSON ключ
6. Конвертируйте в base64:
   cat key.json | base64 > key_b64.txt
```

### Шаг 5: Настройте .env

```bash
cd ~/Desktop/KudoAiBot
cp .env.example .env
nano .env  # или любой редактор
```

Заполните:
```bash
# Telegram
BOT_TOKEN=ваш_токен_от_BotFather
PUBLIC_URL=https://ваш-домен.com
TELEGRAM_MODE=webhook
PORT=8080

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# YooKassa
YOOKASSA_SHOP_ID=ваш_shop_id
YOOKASSA_SECRET_KEY=ваш_secret_key

# Google Cloud
GCP_PROJECT_ID=ваш-project-id
GCP_KEY_JSON_B64=ваш_base64_ключ
GOOGLE_CLOUD_LOCATION=us-central1
```

### Шаг 6: Установите зависимости

```bash
cd ~/Desktop/KudoAiBot
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Шаг 7: Запустите бота!

**Для разработки (polling):**
```bash
export TELEGRAM_MODE=polling
python main.py
```

**Для продакшена (webhook):**
```bash
export TELEGRAM_MODE=webhook
python main.py
```

## ✅ Проверка работы

1. Найдите бота в Telegram
2. Отправьте `/start`
3. Должно появиться приветствие
4. Попробуйте `/balance`
5. Попробуйте `/tariffs`

## 🚀 Деплой на Railway

```bash
# 1. Установите Railway CLI
npm install -g @railway/cli

# 2. Войдите
railway login

# 3. Создайте проект
railway init

# 4. Добавьте PostgreSQL
railway add

# 5. Настройте переменные
railway variables set BOT_TOKEN=ваш_токен
railway variables set YOOKASSA_SHOP_ID=ваш_id
# ... и так далее

# 6. Деплой!
railway up
```

## 🐳 Деплой через Docker

```bash
# 1. Соберите образ
docker build -t kudoaibot .

# 2. Запустите
docker run -d \
  --name kudoaibot \
  -e BOT_TOKEN=ваш_токен \
  -e DATABASE_URL=ваш_database_url \
  -p 8080:8080 \
  kudoaibot
```

## 🔧 Частые проблемы

### Бот не отвечает
```bash
# Проверьте логи
tail -f logs/bot.log

# Проверьте подключение к БД
psql $DATABASE_URL -c "SELECT 1"

# Проверьте webhook
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Ошибка подключения к БД
```bash
# Проверьте формат DATABASE_URL
echo $DATABASE_URL

# Должно быть:
# postgresql://user:password@host:5432/database
```

### YooKassa не работает
```bash
# Проверьте настройки
echo $YOOKASSA_SHOP_ID
echo $YOOKASSA_SECRET_KEY

# Проверьте webhook в личном кабинете YooKassa
```

### Veo 3 не генерирует видео
```bash
# Проверьте Google Cloud настройки
echo $GCP_PROJECT_ID
echo $GCP_KEY_JSON_B64 | base64 -d | jq .

# Проверьте квоты в Google Cloud Console
```

## 📞 Поддержка

Если что-то не работает:

1. **Проверьте логи:**
   ```bash
   python main.py 2>&1 | tee bot.log
   ```

2. **Проверьте переменные:**
   ```bash
   env | grep -E "BOT_TOKEN|DATABASE_URL|YOOKASSA|GCP"
   ```

3. **Проверьте зависимости:**
   ```bash
   pip list | grep -E "aiogram|asyncpg|yookassa"
   ```

## 🎉 Готово!

Ваш бот работает! Теперь можно:
- ✅ Генерировать видео через Veo 3
- ✅ Использовать виртуальную примерочную
- ✅ Принимать платежи через YooKassa
- ✅ Управлять подписками и монетками

**Удачи! 🚀**

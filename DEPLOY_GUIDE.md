# 🚀 Пошаговый деплой на GitHub и Railway

## Часть 1: Подготовка проекта

### Шаг 1: Создайте .gitignore (уже есть)
Проверьте, что файл `.gitignore` содержит:
```
.env
.env.local
__pycache__/
*.pyc
*.db
*.log
.DS_Store
```

### Шаг 2: Создайте файл railway.json
```bash
cd ~/Desktop/KudoAiBot
```

Создайте файл `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
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

---

## Часть 2: Загрузка на GitHub

### Шаг 1: Инициализируйте Git репозиторий
```bash
cd ~/Desktop/KudoAiBot
git init
```

### Шаг 2: Добавьте файлы в Git
```bash
git add .
git commit -m "Initial commit: KudoAiBot v1.0"
```

### Шаг 3: Создайте репозиторий на GitHub

1. **Откройте браузер** → https://github.com
2. **Войдите** в свой аккаунт
3. Нажмите **"+" (плюс)** в правом верхнем углу
4. Выберите **"New repository"**

**Заполните форму:**
```
Repository name:        KudoAiBot
Description:            AI Telegram bot with Veo 3 and Virtual Try-On
Public/Private:         Private (рекомендуется)
Initialize:             НЕ ставьте галочки (README, .gitignore уже есть)
```

5. Нажмите **"Create repository"**

### Шаг 4: Подключите локальный репозиторий к GitHub

GitHub покажет команды. Выполните:
```bash
git remote add origin https://github.com/ВАШ_USERNAME/KudoAiBot.git
git branch -M main
git push -u origin main
```

**Если попросит авторизацию:**
- Username: ваш GitHub username
- Password: используйте **Personal Access Token** (не обычный пароль!)

**Как создать Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → Classic
3. Name: "Railway Deploy"
4. Expiration: 90 days
5. Scopes: выберите `repo` (все галочки)
6. Generate token
7. **СКОПИРУЙТЕ токен** (больше не увидите!)

---

## Часть 3: Деплой на Railway

### Шаг 1: Создайте аккаунт на Railway

1. Откройте https://railway.app
2. Нажмите **"Login"**
3. Выберите **"Login with GitHub"**
4. Авторизуйте Railway

### Шаг 2: Создайте новый проект

1. На главной странице Railway нажмите **"New Project"**
2. Выберите **"Deploy from GitHub repo"**
3. Выберите репозиторий **"KudoAiBot"**
4. Нажмите **"Deploy Now"**

### Шаг 3: Добавьте PostgreSQL

1. В вашем проекте нажмите **"+ New"**
2. Выберите **"Database"**
3. Выберите **"Add PostgreSQL"**
4. Railway автоматически создаст базу данных

### Шаг 4: Настройте переменные окружения

1. Выберите ваш сервис (KudoAiBot)
2. Перейдите на вкладку **"Variables"**
3. Нажмите **"+ New Variable"** для каждой переменной

**Обязательные переменные:**

```bash
# 1. Telegram Bot
BOT_TOKEN
Значение: получите от @BotFather в Telegram
Пример: 7253948572:AAHvB8kX9Qz3L_example_token

# 2. Railway предоставит автоматически
DATABASE_URL
Значение: автоматически (из PostgreSQL сервиса)

# 3. Public URL
PUBLIC_URL
Значение: будет после первого деплоя
Формат: https://kudoaibot-production.up.railway.app

# 4. Telegram Mode
TELEGRAM_MODE
Значение: webhook

# 5. Port
PORT
Значение: 8080

# 6. YooKassa (для платежей)
YOOKASSA_SHOP_ID
Значение: получите на yookassa.ru
Пример: 123456

YOOKASSA_SECRET_KEY
Значение: получите на yookassa.ru
Пример: live_qwerty1234567890abcdef

# 7. Google Cloud Platform (для Veo 3 и Virtual Try-On)
GCP_PROJECT_ID
Значение: ваш проект в Google Cloud
Пример: kudoai-bot-123456

GCP_KEY_JSON_B64
Значение: base64 закодированный JSON ключ сервисного аккаунта
Как получить - см. ниже

GOOGLE_CLOUD_LOCATION
Значение: us-central1

VEO_MODEL
Значение: veo-3.0-fast-generate-001

# 8. Дополнительные настройки
HTTP_TIMEOUT
Значение: 60

HTTP_RETRIES
Значение: 3

TRYON_HTTP_TIMEOUT
Значение: 240

DOWNLOAD_VIDEOS
Значение: 1
```

### Шаг 5: Получите PUBLIC_URL

1. После первого деплоя Railway присвоит URL
2. В настройках сервиса найдите **"Settings"** → **"Networking"**
3. Нажмите **"Generate Domain"**
4. Скопируйте URL (например: `kudoaibot-production.up.railway.app`)
5. Добавьте `https://` в начало
6. Обновите переменную `PUBLIC_URL`:
   ```
   PUBLIC_URL = https://kudoaibot-production.up.railway.app
   ```

### Шаг 6: Подключите DATABASE_URL

1. Если Railway не подключил автоматически:
2. Перейдите в PostgreSQL сервис
3. Вкладка **"Connect"**
4. Скопируйте **"Postgres Connection URL"**
5. В настройках KudoAiBot добавьте переменную:
   ```
   DATABASE_URL = postgresql://postgres:password@host:port/database
   ```

---

## Часть 4: Настройка интеграций

### Telegram Bot (@BotFather)

1. Откройте Telegram, найдите **@BotFather**
2. Отправьте `/newbot`
3. Введите название: `KudoAiBot`
4. Введите username: `kudoai_bot` (или любой доступный)
5. Получите токен
6. Сохраните в Railway как `BOT_TOKEN`

**Настройте webhook:**
```
/setwebhook
Выберите бота
URL: https://kudoaibot-production.up.railway.app/webhook
```

### YooKassa (платежи)

1. Зайдите на https://yookassa.ru
2. **Регистрация:**
   - Создайте магазин
   - Заполните данные компании (ИП или ООО)
   - Дождитесь модерации (~1-2 дня)

3. **Получите ключи:**
   - Личный кабинет → Интеграция
   - Скопируйте **Shop ID**
   - Создайте **Secret Key** (test или live)

4. **Настройте webhook:**
   - Интеграция → HTTP-уведомления
   - URL: `https://kudoaibot-production.up.railway.app/yookassa_webhook`
   - Выберите события: `payment.succeeded`, `payment.canceled`

5. Добавьте в Railway:
   ```
   YOOKASSA_SHOP_ID = ваш_shop_id
   YOOKASSA_SECRET_KEY = ваш_secret_key
   ```

### Google Cloud Platform (Veo 3 и Virtual Try-On)

1. **Создайте проект:**
   - https://console.cloud.google.com
   - Новый проект → "KudoAiBot"
   - Скопируйте Project ID

2. **Включите API:**
   - APIs & Services → Enable APIs
   - Найдите: "Vertex AI API"
   - Нажмите "Enable"

3. **Создайте Service Account:**
   - IAM & Admin → Service Accounts
   - Create Service Account
   - Name: "kudoaibot-service"
   - Role: "Vertex AI User"
   - Create and Continue

4. **Создайте ключ:**
   - Выберите созданный аккаунт
   - Keys → Add Key → Create new key
   - Type: JSON
   - Create (скачается файл `key.json`)

5. **Конвертируйте в Base64:**
   ```bash
   # На macOS/Linux:
   cat ~/Downloads/key.json | base64 | tr -d '\n' > key_b64.txt
   
   # Теперь скопируйте содержимое key_b64.txt
   cat key_b64.txt
   ```

6. **Создайте GCS Bucket (опционально):**
   - Cloud Storage → Create Bucket
   - Name: "kudoaibot-videos"
   - Location: us-central1
   - Storage class: Standard

7. Добавьте в Railway:
   ```
   GCP_PROJECT_ID = ваш-project-id
   GCP_KEY_JSON_B64 = очень_длинная_base64_строка
   GOOGLE_CLOUD_LOCATION = us-central1
   VEO_OUTPUT_GCS_URI = gs://kudoaibot-videos/ (опционально)
   ```

---

## Часть 5: Проверка деплоя

### Шаг 1: Проверьте логи Railway

1. В Railway откройте ваш сервис
2. Перейдите на вкладку **"Deployments"**
3. Выберите последний деплой
4. Нажмите **"View Logs"**

**Что должно быть в логах:**
```
✅ Подключение к базе данных установлено
✅ Таблицы базы данных созданы/обновлены
✅ YooKassa настроена
✅ Webhook установлен
✅ Бот запущен в режиме webhook на порту 8080
```

### Шаг 2: Проверьте базу данных

1. В Railway откройте PostgreSQL
2. Вкладка **"Data"**
3. Должны быть таблицы:
   - users
   - subscriptions
   - transactions
   - generations
   - payments

### Шаг 3: Тестируйте бота

1. Найдите бота в Telegram по username
2. Отправьте `/start`
3. Должно появиться приветствие
4. Попробуйте `/balance`
5. Попробуйте `/tariffs`

---

## Часть 6: Обновление бота

### Когда вы изменили код:

```bash
cd ~/Desktop/KudoAiBot

# 1. Сохраните изменения
git add .
git commit -m "Описание изменений"

# 2. Отправьте на GitHub
git push origin main

# 3. Railway автоматически задеплоит!
```

Railway автоматически отслеживает изменения в GitHub и деплоит новые версии.

---

## 🔧 Решение проблем

### Проблема: Бот не отвечает

**Проверьте:**
1. Railway логи (есть ли ошибки?)
2. Webhook в @BotFather установлен?
3. PUBLIC_URL правильный?

**Решение:**
```bash
# Проверьте webhook через API Telegram
curl https://api.telegram.org/bot<ВАШ_TOKEN>/getWebhookInfo
```

### Проблема: База данных не подключается

**Проверьте:**
1. DATABASE_URL правильный?
2. PostgreSQL сервис запущен?

**Решение:**
В Railway → PostgreSQL → Connect → скопируйте новый URL

### Проблема: YooKassa не работает

**Проверьте:**
1. Webhook настроен в личном кабинете?
2. URL правильный?
3. Ключи test или live?

**Решение:**
Проверьте логи YooKassa в личном кабинете

### Проблема: Veo 3 не генерирует видео

**Проверьте:**
1. GCP_KEY_JSON_B64 правильный?
2. Vertex AI API включен?
3. Есть ли квоты?

**Решение:**
Google Cloud Console → Quotas → проверьте лимиты

---

## 💰 Стоимость Railway

**Бесплатный план:**
- $5 кредитов в месяц
- Достаточно для тестирования
- ~500 часов работы

**Платный план:**
- Pay as you go
- ~$5-10/месяц для небольшого бота
- ~$20-30/месяц для среднего бота

**Оптимизация:**
- Используйте один сервис (не несколько)
- Настройте auto-sleep при неактивности
- Мониторьте использование в Dashboard

---

## ✅ Чеклист деплоя

- [ ] Git инициализирован
- [ ] Код загружен на GitHub
- [ ] Railway проект создан
- [ ] PostgreSQL добавлен
- [ ] Все переменные окружения настроены
- [ ] PUBLIC_URL получен и добавлен
- [ ] Telegram webhook настроен
- [ ] YooKassa webhook настроен
- [ ] Google Cloud настроен
- [ ] Бот протестирован

---

## 🎉 Готово!

Ваш бот теперь работает в облаке! 

**Полезные ссылки:**
- Railway Dashboard: https://railway.app/dashboard
- GitHub Repo: https://github.com/ВАШ_USERNAME/KudoAiBot
- Telegram Bot: @ваш_бот_username

**Поддержка:**
- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app

Удачи! 🚀

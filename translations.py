"""
🌍 Мультиязычная система для SORA 2 от Neurokudo
Поддержка 5 языков: Русский, Английский, Испанский, Арабский, Хинди
"""

LANG = {
    "ru": {
        # Основные сообщения
        "welcome": "👋 Привет, {name}! Это <b>SORA 2 от Neurokudo</b>.\n\n🎬 <b>Твой тариф:</b> {plan}\n🎞 <b>Осталось видео:</b> {videos_left}\n\n🔥 <b>Создавай крутые вирусные видео и радуй друзей и подписчиков!</b>\n\n📖 <a href='https://github.com/Neurokudo/sora2kudo-bot/blob/main/INSTRUCTION.md'>Инструкция</a> — как пользоваться ботом",
        "choose_action": "💡 <b>Выбери действие:</b>",
        "choose_language": "🌍 <b>Выберите язык:</b>",
        "lang_selected": "✅ <b>Язык изменён на Русский.</b>",
        "help": "Опиши свою идею — и я помогу превратить её в видео.",
        
        # Меню и кнопки
        "btn_create_video": "🎬 Создать видео",
        "btn_examples": "📘 Примеры", 
        "btn_profile": "👤 Профиль",
        "btn_help": "❓ Помощь",
        "btn_language": "🌍 Язык",
        
        # Ориентация видео
        "choose_orientation": "📐 <b>Выбери ориентацию для будущих видео:</b>",
        "orientation_vertical": "📱 Вертикальное",
        "orientation_horizontal": "🖥 Горизонтальное",
        "btn_main_menu": "🏠 Главное меню",
        "video_confirmation": "📝 <b>Подтверждение создания видео</b>\n\n🎬 <b>Ваш запрос:</b> {description}\n📐 <b>Ориентация:</b> {orientation}\n🎞 <b>Осталось видео:</b> {videos_left}\n\n✅ <b>Все верно?</b>",
        "btn_create_confirm": "Создать ✅",
        "btn_edit_request": "Изменить 📝", 
        "btn_cancel_request": "Отмена ↩️",
                "orientation_selected": "📐 <b>Выбрана {orientation} ориентация</b>\n\n📝 <b>Опиши сцену простыми словами и отправь ее в чат:</b>\nКто в кадре, где происходит действие, что они делают, какая атмосфера и погода.\nДобавь, если нужно, детали: одежду, эмоции, свет, фон.\n\n💡 <b>Пример:</b>\n<code>Рыбаки поймали в лодку русалкоподобное чудище, рыбак в тельняшке и камуфляжных штанах, тянут ее сетью, чудище женоподобное, вырывается и шипит, съёмка на телефон, грудь покрыта плотной чешуей, склизкая, вся в тине.</code>",
        "orientation_vertical_name": "вертикальная",
        "orientation_horizontal_name": "горизонтальная",
        
        # Создание видео
                "create_video": "🎬 <b>Создание видео</b>\n\n📐 Ориентация: <b>{orientation}</b>\n🎞 Осталось видео: <b>{videos_left}</b>\n\n✏️ <b>Опиши сцену простыми словами:</b>\nКто в кадре, где происходит действие, что они делают, какая атмосфера и погода.\nДобавь, если нужно, детали: одежду, эмоции, свет, фон.\n\n📸 <b>Пример:</b>\n<code>Рыбаки поймали в лодку русалкоподобное чудище, рыбак в тельняшке и камуфляжных штанах, тянут ее сетью, чудище женоподобное, вырывается и шипит, съёмка на телефон, грудь покрыта плотной чешуей, склизкая, вся в тине.</code>",
                "video_accepted": "🎬 <b>Принято описание!</b>\n\n📝 <b>Описание:</b> {description}\n📐 <b>Ориентация:</b> {orientation}\n🎞 <b>Осталось видео:</b> {videos_left}\n\n⏳ <b>Ваше видео отправлено в очередь на создание...</b>",
                "video_ready": "🎉 <b>Ваше видео готово!</b>\n\n🎬 Видео успешно создано через Sora 2\n📹 <b>Видео отправлено в чат выше</b>\n🎞 Осталось видео: <b>{videos_left}</b>\n\n💡 Для продолжения создания пришлите новое описание!",
                "video_creating": "🎬 <b>Создание видео...</b>\n\n⏳ Обрабатываем ваше описание через Sora 2\n🔄 Это может занять 2-3 минуты\n\n📹 Видео будет отправлено в этот чат как только будет готово!",
                "video_error": "❌ <b>Ошибка создания видео</b>\n\n⚠️ Не удалось создать видео по вашему описанию\n🔄 Попробуйте изменить описание или обратитесь в поддержку\n\n🎞 Осталось видео: <b>{videos_left}</b>",
                "no_videos_left": "😢 <b>Ой-ой! У тебя закончились видео!</b>\n\n💔 Больше не можешь создавать крутые ролики...\n🎬 Но не расстраивайся!\n\n💎 <b>Выбери тариф и продолжай творить:</b>\n🌱 <b>Пробный</b> — 3 видео за ₽390\n✨ <b>Базовый</b> — 10 видео за ₽990\n💎 <b>Максимум</b> — 30 видео за ₽2,190\n\n🔥 <b>Создавай вирусные видео и радуй друзей!</b>",
        
        # Примеры
        "examples": "📘 <b>Примеры идей для видео:</b>\n\n🔹 Рыбаки вытаскивают сеть, в ней странное существо\n🔹 Грибники находят движущуюся массу под листьями\n🔹 Бабушка кормит капибару у окна, рассвет\n🔹 Советские рабочие открывают капсулу времени\n🔹 Дети находят портал в другой мир\n🔹 Старый дом с привидениями, ночь\n\n💡 <b>Теперь создавай свое видео!</b>",
        
        # Профиль
        "profile": "💰 <b>Твой кабинет</b>\n\n👤 Имя: <b>{name}</b>\n📦 Тариф: <b>{plan}</b>\n🎞 Осталось видео: <b>{videos_left}</b>\n📅 Регистрация: <b>{date}</b>\n\n🔁 <b>Нужно больше видео?</b>\nВыбери подходящий тариф:\n\n🌱 <b>Пробный</b> — 3 видео за ₽390\n✨ <b>Базовый</b> — 10 видео за ₽990\n💎 <b>Максимум</b> — 30 видео за ₽2,190",
        
        # Помощь
        "help_text": "🧭 <b>Помощь</b>\n\nЕсли бот работает некорректно или кнопка не реагирует — просто напиши об этом ниже, я получу сообщение и проверю как можно скорее.\n\n⚠️ <b>Обрати внимание:</b> за результат видео я не несу ответственности — генерация выполняется на стороне нейросети и может отличаться от ожиданий. Если ролик получился не так, как хотелось, просто попробуй изменить запрос.\n\n📄 <b>Оферта:</b> https://disk.yandex.ru/i/dj2ZgY22d5MRtA\n\n(ссылка также есть в описании бота)",
        "support_sent": "✅ Сообщение отправлено. Я постараюсь ответить как можно скорее!",
        
        # Кнопки покупки тарифов
        "btn_buy_trial": "🌱 Купить Пробный (₽390)",
        "btn_buy_basic": "✨ Купить Базовый (₽990)", 
        "btn_buy_maximum": "💎 Купить Максимум (₽2,190)",
        "btn_buy_foreign": "💳 Иностранная карта",
        "btn_buy_tariff": "💳 Купить тариф",
        "tariff_selection": "💳 <b>Выберите тариф для покупки:</b>",
        
        # Сообщения оплаты
        "payment_title": "💳 <b>Оплата тарифа {tariff}</b>",
        "payment_amount": "💰 Сумма: <b>{price} ₽</b>",
        "payment_videos": "🎞 Видео: <b>{videos}</b>",
        "payment_activation": "📱 После оплаты ваш тариф будет автоматически активирован!",
        "payment_button": "💳 ОПЛАТИТЬ",
        "payment_error": "❌ Ошибка создания платежа. Попробуйте позже.",
        "payment_unavailable": "⚠️ Система оплаты временно недоступна.\nПопробуйте позже!",
        "foreign_card_title": "💰 <b>Выберите ваш план:</b>",
        "foreign_card_description": "🌍 Оплата работает по всему миру — Tribute автоматически конвертирует цену в вашу локальную валюту.\n\nПосле оплаты ваш аккаунт в @sora2kudo_bot будет обновлен автоматически 🎬",
        "foreign_trial": "Пробный",
        "foreign_basic": "Базовый", 
        "foreign_premium": "Максимум",
        "videos": "видео",
        
                # Сообщения для пользователей без тарифа
        "no_tariff_message": "🚀 <b>Начни создавать вирусные видео прямо сейчас!</b>\n\n💎 <b>Выбери тариф и получи доступ к SORA 2:</b>\n🌱 <b>Пробный</b> — 3 видео за ₽390\n✨ <b>Базовый</b> — 10 видео за ₽990\n💎 <b>Максимум</b> — 30 видео за ₽2,190\n\n🔥 <b>Создавай крутые видео и радуй друзей и подписчиков!</b>",
        "examples_subscription_required": "🔒 <b>Примеры доступны только с подпиской!</b>\n\n💎 <b>Получите доступ к готовым идеям для вирусных видео:</b>\n🌱 <b>Пробный</b> — 3 видео за ₽390\n✨ <b>Базовый</b> — 10 видео за ₽990\n💎 <b>Максимум</b> — 30 видео за ₽2,190\n\n🔥 <b>Создавайте крутые видео и радуйте друзей!</b>",
        
        # Сообщения после генерации видео
        "video_success_title": "🎉 <b>Ваше видео готово!</b>",
        "video_success_message": "🎞 <b>Осталось видео:</b> {videos_left}\n\n✏️ <b>Для создания нового видео пришлите новый запрос</b>",
        "btn_change_orientation": "📐 Сменить ориентацию",
        
        # Сообщения об ошибках Sora 2
        "sora_error_title": "😔 <b>Мы не можем создать такое видео, данный запрос нарушает правила Sora 2</b>",
        "sora_error_rules": "📖 <b>Более подробно о правилах:</b> https://openai.com/policies/usage-policies",
        "sora_error_refund": "💰 <b>Видео возвращено на баланс</b>\n🎞 <b>Осталось видео:</b> {videos_left}",
        
        # Общие фразы
        "use_buttons": "💡 Используй кнопки меню ниже для навигации!",
        "error_restart": "❌ Ошибка. Попробуй /start",
        "error_getting_data": "❌ Ошибка получения данных. Попробуй /start",
    },
    
    "en": {
        # Основные сообщения
        "welcome": "👋 Hi, {name}! This is <b>SORA 2 by Neurokudo</b>.\n\n🎬 <b>Your tariff:</b> {plan}\n🎞 <b>Videos left:</b> {videos_left}\n\n🔥 <b>Create amazing viral videos and delight your friends and followers!</b>\n\n📖 <a href='https://github.com/Neurokudo/sora2kudo-bot/blob/main/INSTRUCTION.md'>Instruction</a> — how to use the bot",
        "choose_action": "💡 <b>Choose an action:</b>",
        "choose_language": "🌍 <b>Choose your language:</b>",
        "lang_selected": "✅ <b>Language set to English.</b>",
        "help": "Describe your idea — and I'll help turn it into a video.",
        
        # Меню и кнопки
        "btn_create_video": "🎬 Create Video",
        "btn_examples": "📘 Examples", 
        "btn_profile": "👤 Profile",
        "btn_help": "❓ Help",
        "btn_language": "🌍 Language",
        
        # Ориентация видео
        "choose_orientation": "📐 <b>Choose orientation for future videos:</b>",
        "orientation_vertical": "📱 Vertical",
        "orientation_horizontal": "🖥 Horizontal",
        "btn_main_menu": "🏠 Main Menu",
        "btn_cancel": "❌ Cancel",
                "orientation_selected": "✅ <b>{orientation} orientation selected</b>\n\n🎬 <b>Describe the scene in simple words:</b>\nWho is in the frame, where the action takes place, what they are doing, atmosphere and weather.\nAdd details if needed: clothing, emotions, lighting, background.\n\n📸 <b>Example:</b>\n<code>Fishermen caught a mermaid-like creature in a boat, fisherman in striped shirt and camo pants pulls the net, creature is feminine, struggles and hisses, phone recording, chest covered with dense scales, slimy, covered in mud.</code>",
        "orientation_vertical_name": "vertical",
        "orientation_horizontal_name": "horizontal",
        
        # Создание видео
                "create_video": "🎬 <b>Creating Video</b>\n\n📐 Orientation: <b>{orientation}</b>\n🎞 Videos left: <b>{videos_left}</b>\n\n✏️ <b>Describe the scene in simple words:</b>\nWho is in the frame, where the action takes place, what they are doing, atmosphere and weather.\nAdd details if needed: clothing, emotions, lighting, background.\n\n📸 <b>Example:</b>\n<code>Fishermen caught a mermaid-like creature in a boat, fisherman in striped shirt and camo pants pulls the net, creature is feminine, struggles and hisses, phone recording, chest covered with dense scales, slimy, covered in mud.</code>",
                "video_accepted": "🎬 <b>Description accepted!</b>\n\n📝 <b>Description:</b> {description}\n📐 <b>Orientation:</b> {orientation}\n🎞 <b>Videos left:</b> {videos_left}\n\n⏳ <b>Your video has been queued for creation...</b>",
                "video_ready": "🎉 <b>Your video is ready!</b>\n\n🎬 Video successfully created via Sora 2\n📹 <b>Video sent to chat above</b>\n🎞 Videos left: <b>{videos_left}</b>\n\n💡 To continue creating, send a new description!",
                "video_creating": "🎬 <b>Creating video...</b>\n\n⏳ Processing your description through Sora 2\n🔄 This may take 2-3 minutes\n\n📹 Video will be sent to this chat once ready!",
                "video_error": "❌ <b>Video creation error</b>\n\n⚠️ Could not create video from your description\n🔄 Try changing the description or contact support\n\n🎞 Videos left: <b>{videos_left}</b>",
                "no_videos_left": "😢 <b>Oops! You're out of videos!</b>\n\n💔 Can't create cool videos anymore...\n🎬 But don't worry!\n\n💎 <b>Choose a tariff and keep creating:</b>\n🌱 <b>Trial</b> — 3 videos for ₽390\n✨ <b>Basic</b> — 10 videos for ₽990\n💎 <b>Maximum</b> — 30 videos for ₽2,190\n\n🔥 <b>Create viral videos and delight your friends!</b>",
        
        # Примеры
        "examples": "📘 <b>Video idea examples:</b>\n\n🔹 Fishermen pulling a net with strange creature\n🔹 Mushroom pickers find moving mass under leaves\n🔹 Grandma feeding capybara by window at dawn\n🔹 Soviet workers opening time capsule\n🔹 Children finding portal to another world\n🔹 Old haunted house at night\n\n💡 <b>Now create your video!</b>",
        
        # Профиль
        "profile": "💰 <b>Your Profile</b>\n\n👤 Name: <b>{name}</b>\n📦 Plan: <b>{plan}</b>\n🎞 Videos left: <b>{videos_left}</b>\n📅 Registration: <b>{date}</b>\n\n🔁 <b>Need more videos?</b>\nChoose a suitable tariff:\n\n🌱 <b>Trial</b> — 3 videos for ₽390\n✨ <b>Basic</b> — 10 videos for ₽990\n💎 <b>Maximum</b> — 30 videos for ₽2,190",
        
        # Помощь
        "help_text": "🧭 <b>Help</b>\n\nDescribe your problem, I'll try to help soon!",
        "support_sent": "✅ Message sent. I'll try to respond as soon as possible!",
        
        # Кнопки покупки тарифов
        "btn_buy_trial": "🌱 Buy Trial (₽390)",
        "btn_buy_basic": "✨ Buy Basic (₽990)", 
        "btn_buy_maximum": "💎 Buy Maximum (₽2,190)",
        "btn_buy_foreign": "💳 Foreign Card",
        "btn_buy_tariff": "💳 Buy tariff",
        "tariff_selection": "💳 <b>Choose tariff to purchase:</b>",
        
        # Сообщения оплаты
        "payment_title": "💳 <b>Payment for {tariff}</b>",
        "payment_amount": "💰 Amount: <b>{price} ₽</b>",
        "payment_videos": "🎞 Videos: <b>{videos}</b>",
        "payment_activation": "📱 After payment, your tariff will be automatically activated!",
        "payment_button": "💳 PAY",
        "payment_error": "❌ Payment creation error. Please try again later.",
        "payment_unavailable": "⚠️ Payment system temporarily unavailable.\nPlease try again later!",
        "foreign_card_title": "💰 <b>Choose your plan:</b>",
        "foreign_card_description": "🌍 Payment works worldwide — Tribute automatically converts the price to your local currency.\n\nAfter payment, your account in @sora2kudo_bot will be updated automatically 🎬",
        "foreign_trial": "Trial",
        "foreign_basic": "Basic", 
        "foreign_premium": "Maximum",
        "videos": "videos",
        
                # Сообщения для пользователей без тарифа
        "no_tariff_message": "🚀 <b>Start creating viral videos right now!</b>\n\n💎 <b>Choose a tariff and get access to SORA 2:</b>\n🌱 <b>Trial</b> — 3 videos for ₽390\n✨ <b>Basic</b> — 10 videos for ₽990\n💎 <b>Maximum</b> — 30 videos for ₽2,190\n\n🔥 <b>Create amazing videos and delight your friends and followers!</b>",
        "examples_subscription_required": "🔒 <b>Examples available only with subscription!</b>\n\n💎 <b>Get access to ready-made ideas for viral videos:</b>\n🌱 <b>Trial</b> — 3 videos for ₽390\n✨ <b>Basic</b> — 10 videos for ₽990\n💎 <b>Maximum</b> — 30 videos for ₽2,190\n\n🔥 <b>Create amazing videos and delight your friends!</b>",
        
        # Сообщения после генерации видео
        "video_success_title": "🎉 <b>Your video is ready!</b>",
        "video_success_message": "🎞 <b>Videos left:</b> {videos_left}\n\n💡 <b>To create a new video, send a new request ✍️</b>",
        "btn_change_orientation": "📐 Change Orientation",
        
        # Сообщения об ошибках Sora 2
        "sora_error_title": "😔 <b>We cannot create this video, this request violates Sora 2 rules</b>",
        "sora_error_rules": "📖 <b>More details about the rules:</b> https://openai.com/policies/usage-policies",
        "sora_error_refund": "💰 <b>Video returned to balance</b>\n🎞 <b>Videos left:</b> {videos_left}",
        
        # Общие фразы
        "use_buttons": "💡 Use menu buttons or choose video orientation!",
        "error_restart": "❌ Error. Try /start",
        "error_getting_data": "❌ Error getting data. Try /start",
    },
    
    "es": {
        # Основные сообщения
        "welcome": "👋 ¡Hola, {name}! Este es <b>SORA 2 de Neurokudo</b>.\n\n🎬 <b>Tu plan:</b> {plan}\n🎞 <b>Videos restantes:</b> {videos_left}\n\n🔥 <b>¡Crea videos virales increíbles y deleita a tus amigos y seguidores!</b>\n\n📖 <a href='https://github.com/Neurokudo/sora2kudo-bot/blob/main/INSTRUCTION.md'>Instrucción</a> — cómo usar el bot",
        "choose_action": "💡 <b>Elige una acción:</b>",
        "choose_language": "🌍 <b>Elige tu idioma:</b>",
        "lang_selected": "✅ <b>Idioma cambiado a Español.</b>",
        "help": "Describe tu idea y la convertiré en video.",
        
        # Меню и кнопки
        "btn_create_video": "🎬 Crear Video",
        "btn_examples": "📘 Ejemplos", 
        "btn_profile": "👤 Perfil",
        "btn_help": "❓ Ayuda",
        "btn_language": "🌍 Idioma",
        
        # Ориентация видео
        "choose_orientation": "📐 <b>Elige orientación para futuros videos:</b>",
        "orientation_vertical": "📱 Vertical",
        "orientation_horizontal": "🖥 Horizontal",
        "btn_main_menu": "🏠 Menú Principal",
        "btn_cancel": "❌ Cancelar",
        "orientation_selected": "✅ <b>Orientación {orientation} seleccionada</b>\n\n¡Ahora presiona <b>🎬 Crear Video</b> y describe lo que quieres filmar!",
        "orientation_vertical_name": "vertical",
        "orientation_horizontal_name": "horizontal",
        
        # Создание видео
        "create_video": "🎬 <b>Creando Video</b>\n\n📐 Orientación: <b>{orientation}</b>\n🎞 Videos restantes: <b>{videos_left}</b>\n\n✏️ <b>Describe lo que quieres filmar:</b>\nEjemplo: <code>Pescadores sacando red con sirena adentro</code>",
        "video_accepted": "🎬 <b>¡Descripción aceptada!</b>\n\n📝 <b>Descripción:</b> {description}\n📐 <b>Orientación:</b> {orientation}\n🎞 <b>Videos restantes:</b> {videos_left}\n\n⏳ Video siendo creado via Sora 2...\n📨 ¡El resultado será enviado aquí!",
        "no_videos_left": "🚫 <b>¡Te quedaste sin videos!</b>\n\n💳 Compra nuevo paquete en <b>💰 Perfil</b>",
        
        # Примеры
        "examples": "📘 <b>Ejemplos de ideas para video:</b>\n\n🔹 Pescadores sacando red con criatura extraña\n🔹 Recolectores de hongos encuentran masa móvil bajo hojas\n🔹 Abuela alimentando capibara en ventana al amanecer\n🔹 Trabajadores soviéticos abriendo cápsula del tiempo\n🔹 Niños encontrando portal a otro mundo\n🔹 Casa embrujada vieja en la noche\n\n💡 <b>¡Ahora crea tu video!</b>",
        
        # Профиль
        "profile": "💰 <b>Tu Perfil</b>\n\n👤 Nombre: <b>{name}</b>\n📦 Plan: <b>{plan}</b>\n🎞 Videos restantes: <b>{videos_left}</b>\n📅 Registro: <b>{date}</b>\n\n🔁 <b>¿Necesitas más videos?</b>\nElige paquete:\n🐣 Prueba — 3 videos → ₽390\n🎬 Básico — 10 videos → ₽990\n🚀 Máximo — 30 videos → ₽2,190",
        
        # Помощь
        "help_text": "🧭 <b>Ayuda</b>\n\nDescribe tu problema, ¡trataré de ayudar pronto!",
        "support_sent": "✅ Mensaje enviado. ¡Trataré de responder lo antes posible!",
        
        # Кнопки покупки тарифов
        "btn_buy_trial": "🌱 Comprar Prueba (₽390)",
        "btn_buy_basic": "✨ Comprar Básico (₽990)", 
        "btn_buy_maximum": "💎 Comprar Máximo (₽2,190)",
        "btn_buy_foreign": "💳 Tarjeta Extranjera",
        
        # Сообщения оплаты
        "payment_title": "💳 <b>Pago de {tariff}</b>",
        "payment_amount": "💰 Cantidad: <b>{price} ₽</b>",
        "payment_videos": "🎞 Videos: <b>{videos}</b>",
        "payment_activation": "📱 ¡Después del pago, tu tarifa se activará automáticamente!",
        "payment_button": "💳 PAGAR",
        "payment_error": "❌ Error al crear el pago. Inténtalo más tarde.",
        "payment_unavailable": "⚠️ Sistema de pago temporalmente no disponible.\n¡Inténtalo más tarde!",
        "foreign_card_title": "💰 <b>Elige tu plan:</b>",
        "foreign_card_description": "🌍 El pago funciona en todo el mundo — Tribute convierte automáticamente el precio a tu moneda local.\n\nDespués del pago, tu cuenta en @sora2kudo_bot se actualizará automáticamente 🎬",
        "foreign_trial": "Prueba",
        "foreign_basic": "Básico",
        "foreign_premium": "Máximo",
        "videos": "videos",
        
        # Сообщения для пользователей без тарифа
        "no_tariff_message": "🚀 <b>¡Comienza a crear videos virales ahora mismo!</b>\n\n💎 <b>Elige una tarifa y obtén acceso a SORA 2:</b>\n🌱 <b>Prueba</b> — 3 videos por ₽390\n✨ <b>Básico</b> — 10 videos por ₽990\n💎 <b>Máximo</b> — 30 videos por ₽2,190\n\n🔥 <b>¡Crea videos increíbles y deleita a tus amigos y seguidores!</b>",
        "examples_subscription_required": "🔒 <b>¡Ejemplos disponibles solo con suscripción!</b>\n\n💎 <b>Obtén acceso a ideas listas para videos virales:</b>\n🌱 <b>Prueba</b> — 3 videos por ₽390\n✨ <b>Básico</b> — 10 videos por ₽990\n💎 <b>Máximo</b> — 30 videos por ₽2,190\n\n🔥 <b>¡Crea videos increíbles y deleita a tus amigos!</b>",
        
        # Дополнительные ключи
        "btn_buy_tariff": "💳 Comprar tarifa",
        "tariff_selection": "💳 <b>Elige tarifa para comprar:</b>",
        "video_creating": "🎬 <b>Creando video...</b>\n\n⏳ Procesando tu descripción a través de Sora 2\n🔄 Esto puede tomar 2-3 minutos\n\n📹 El video se enviará a este chat cuando esté listo!",
        "video_error": "❌ <b>Error al crear video</b>\n\n⚠️ No se pudo crear el video con tu descripción\n🔄 Intenta cambiar la descripción o contacta soporte\n\n🎞 Videos restantes: <b>{videos_left}</b>",
        "video_ready": "🎉 <b>¡Tu video está listo!</b>\n\n🎬 Video creado exitosamente a través de Sora 2\n📹 <b>Video enviado al chat de arriba</b>\n🎞 Videos restantes: <b>{videos_left}</b>\n\n💡 ¡Para continuar creando, envía una nueva descripción!",
        "video_success_title": "🎉 <b>¡Tu video está listo!</b>",
        "video_success_message": "🎞 <b>Videos restantes:</b> {videos_left}\n\n💡 <b>Para crear un nuevo video, envía una nueva solicitud ✍️</b>",
        "btn_change_orientation": "📐 Cambiar Orientación",
        
        # Сообщения об ошибках Sora 2
        "sora_error_title": "😔 <b>No podemos crear este video, esta solicitud viola las reglas de Sora 2</b>",
        "sora_error_rules": "📖 <b>Más detalles sobre las reglas:</b> https://openai.com/policies/usage-policies",
        "sora_error_refund": "💰 <b>Video devuelto al saldo</b>\n🎞 <b>Videos restantes:</b> {videos_left}",
        
        # Общие фразы
        "use_buttons": "💡 ¡Usa botones del menú o elige orientación de video!",
        "error_restart": "❌ Error. Prueba /start",
        "error_getting_data": "❌ Error obteniendo datos. Prueba /start",
    },
    
    "ar": {
        # Основные сообщения
        "welcome": "👋 مرحباً {name}! هذا هو <b>SORA 2 من Neurokudo</b>.\n\n🎬 <b>خطتك:</b> {plan}\n🎞 <b>الفيديوهات المتبقية:</b> {videos_left}\n\n🔥 <b>أنشئ فيديوهات فيروسية رائعة وأسعد أصدقاءك ومتابعيك!</b>\n\n📖 <a href='https://github.com/Neurokudo/sora2kudo-bot/blob/main/INSTRUCTION.md'>تعليمات</a> — كيفية استخدام البوت",
        "choose_action": "💡 <b>اختر إجراء:</b>",
        "choose_language": "🌍 <b>اختر لغتك:</b>",
        "lang_selected": "✅ <b>تم تغيير اللغة إلى العربية.</b>",
        "help": "صف فكرتك وسأحولها إلى فيديو.",
        
        # Меню и кнопки
        "btn_create_video": "🎬 إنشاء فيديو",
        "btn_examples": "📘 أمثلة", 
        "btn_profile": "👤 الملف الشخصي",
        "btn_help": "❓ مساعدة",
        "btn_language": "🌍 اللغة",
        
        # Ориентация видео
        "choose_orientation": "📐 <b>اختر اتجاه الفيديوهات المستقبلية:</b>",
        "orientation_vertical": "📱 عمودي",
        "orientation_horizontal": "🖥 أفقي",
        "btn_main_menu": "🏠 القائمة الرئيسية",
        "btn_cancel": "❌ إلغاء",
        "orientation_selected": "✅ <b>تم اختيار الاتجاه {orientation}</b>\n\nالآن اضغط <b>🎬 إنشاء فيديو</b> وصف ما تريد تصويره!",
        "orientation_vertical_name": "عمودي",
        "orientation_horizontal_name": "أفقي",
        
        # Создание видео
        "create_video": "🎬 <b>إنشاء فيديو</b>\n\n📐 الاتجاه: <b>{orientation}</b>\n🎞 الفيديوهات المتبقية: <b>{videos_left}</b>\n\n✏️ <b>صف ما تريد تصويره:</b>\nمثال: <code>صيادون يسحبون شبكة بها حورية</code>",
        "video_accepted": "🎬 <b>تم قبول الوصف!</b>\n\n📝 <b>الوصف:</b> {description}\n📐 <b>الاتجاه:</b> {orientation}\n🎞 <b>الفيديوهات المتبقية:</b> {videos_left}\n\n⏳ يتم إنشاء الفيديو عبر Sora 2...\n📨 ستتم إرسال النتيجة هنا!",
        "no_videos_left": "🚫 <b>انتهت فيديوهاتك!</b>\n\n💳 اشتر باقة جديدة في <b>💰 الملف الشخصي</b>",
        
        # Примеры
        "examples": "📘 <b>أمثلة أفكار للفيديو:</b>\n\n🔹 صيادون يسحبون شبكة بها مخلوق غريب\n🔹 جامعو الفطر يجدون كتلة متحركة تحت الأوراق\n🔹 جدة تطعم كابيبارا عند النافذة في الفجر\n🔹 عمال سوفييت يفتحون كبسولة زمنية\n🔹 أطفال يجدون بوابة لعالم آخر\n🔹 منزل مسكون قديم في الليل\n\n💡 <b>الآن أنشئ فيديوك!</b>",
        
        # Профиль
        "profile": "💰 <b>ملفك الشخصي</b>\n\n👤 الاسم: <b>{name}</b>\n📦 الخطة: <b>{plan}</b>\n🎞 الفيديوهات المتبقية: <b>{videos_left}</b>\n📅 التسجيل: <b>{date}</b>\n\n🔁 <b>تحتاج فيديوهات أكثر؟</b>\nاختر باقة:\n🐣 تجريبية — 3 فيديوهات → ₽390\n🎬 أساسية — 10 فيديوهات → ₽990\n🚀 قصوى — 30 فيديو → ₽2,190",
        
        # Помощь
        "help_text": "🧭 <b>مساعدة</b>\n\nصف مشكلتك، سأحاول المساعدة قريباً!",
        "support_sent": "✅ تم إرسال الرسالة. سأحاول الرد في أقرب وقت ممكن!",
        
        # Кнопки покупки тарифов
        "btn_buy_trial": "🌱 اشتر تجريبي (₽390)",
        "btn_buy_basic": "✨ اشتر أساسي (₽990)", 
        "btn_buy_maximum": "💎 اشتر قصوى (₽2,190)",
        "btn_buy_foreign": "💳 بطاقة أجنبية",
        
        # Сообщения оплаты
        "payment_title": "💳 <b>دفع {tariff}</b>",
        "payment_amount": "💰 المبلغ: <b>{price} ₽</b>",
        "payment_videos": "🎞 فيديو: <b>{videos}</b>",
        "payment_activation": "📱 بعد الدفع، سيتم تفعيل خطتك تلقائياً!",
        "payment_button": "💳 دفع",
        "payment_error": "❌ خطأ في إنشاء الدفع. حاول مرة أخرى لاحقاً.",
        "payment_unavailable": "⚠️ نظام الدفع غير متاح مؤقتاً.\nحاول مرة أخرى لاحقاً!",
        "foreign_card_title": "💰 <b>اختر خطتك:</b>",
        "foreign_card_description": "🌍 الدفع يعمل في جميع أنحاء العالم — Tribute يحول السعر تلقائياً إلى عملتك المحلية.\n\nبعد الدفع، سيتم تحديث حسابك في @sora2kudo_bot تلقائياً 🎬",
        "foreign_trial": "تجريبي",
        "foreign_basic": "أساسي",
        "foreign_premium": "قصوى",
        "videos": "فيديو",
        
        # Сообщения для пользователей بدون тарифа
        "no_tariff_message": "🚀 <b>ابدأ إنشاء الفيديوهات الفيروسية الآن!</b>\n\n💎 <b>اختر خطة واحصل على الوصول إلى SORA 2:</b>\n🌱 <b>تجريبي</b> — 3 فيديوهات مقابل ₽390\n✨ <b>أساسي</b> — 10 فيديوهات مقابل ₽990\n💎 <b>قصوى</b> — 30 فيديو مقابل ₽2,190\n\n🔥 <b>أنشئ فيديوهات رائعة وأسعد أصدقاءك ومتابعيك!</b>",
        "examples_subscription_required": "🔒 <b>الأمثلة متاحة فقط مع الاشتراك!</b>\n\n💎 <b>احصل على الوصول إلى أفكار جاهزة للفيديوهات الفيروسية:</b>\n🌱 <b>تجريبي</b> — 3 فيديوهات مقابل ₽390\n✨ <b>أساسي</b> — 10 فيديوهات مقابل ₽990\n💎 <b>قصوى</b> — 30 فيديو مقابل ₽2,190\n\n🔥 <b>أنشئ فيديوهات رائعة وأسعد أصدقاءك!</b>",
        
        # مفاتيح إضافية
        "btn_buy_tariff": "💳 شراء خطة",
        "tariff_selection": "💳 <b>اختر خطة للشراء:</b>",
        "video_creating": "🎬 <b>إنشاء فيديو...</b>\n\n⏳ معالجة وصفك من خلال Sora 2\n🔄 قد يستغرق هذا 2-3 دقائق\n\n📹 سيتم إرسال الفيديو إلى هذه المحادثة عندما يكون جاهزاً!",
        "video_error": "❌ <b>خطأ في إنشاء الفيديو</b>\n\n⚠️ لا يمكن إنشاء الفيديو من وصفك\n🔄 حاول تغيير الوصف أو اتصل بالدعم\n\n🎞 الفيديوهات المتبقية: <b>{videos_left}</b>",
        "video_ready": "🎉 <b>فيديوك جاهز!</b>\n\n🎬 تم إنشاء الفيديو بنجاح من خلال Sora 2\n📹 <b>تم إرسال الفيديو إلى المحادثة أعلاه</b>\n🎞 الفيديوهات المتبقية: <b>{videos_left}</b>\n\n💡 للمتابعة في الإنشاء، أرسل وصفاً جديداً!",
        "video_success_title": "🎉 <b>فيديوك جاهز!</b>",
        "video_success_message": "🎞 <b>الفيديوهات المتبقية:</b> {videos_left}\n\n💡 <b>لإنشاء فيديو جديد، أرسل طلباً جديداً ✍️</b>",
        "btn_change_orientation": "📐 تغيير الاتجاه",
        
        # Сообщения об ошибках Sora 2
        "sora_error_title": "😔 <b>لا يمكننا إنشاء هذا الفيديو، هذا الطلب يخالف قواعد Sora 2</b>",
        "sora_error_rules": "📖 <b>مزيد من التفاصيل حول القواعد:</b> https://openai.com/policies/usage-policies",
        "sora_error_refund": "💰 <b>تم إرجاع الفيديو إلى الرصيد</b>\n🎞 <b>الفيديوهات المتبقية:</b> {videos_left}",
        
        # Общие фразы
        "use_buttons": "💡 استخدم أزرار القائمة أو اختر اتجاه الفيديو!",
        "error_restart": "❌ خطأ. جرب /start",
        "error_getting_data": "❌ خطأ في الحصول على البيانات. جرب /start",
    },
    
    "hi": {
        # Основные сообщения
        "welcome": "👋 नमस्ते {name}! यह है <b>SORA 2 by Neurokudo</b>।\n\n🎬 <b>आपकी योजना:</b> {plan}\n🎞 <b>बचे वीडियो:</b> {videos_left}\n\n🔥 <b>अद्भुत वायरल वीडियो बनाएं और अपने दोस्तों और फॉलोअर्स को खुश करें!</b>\n\n📖 <a href='https://github.com/Neurokudo/sora2kudo-bot/blob/main/INSTRUCTION.md'>निर्देश</a> — बॉट का उपयोग कैसे करें",
        "choose_action": "💡 <b>एक क्रिया चुनें:</b>",
        "choose_language": "🌍 <b>अपनी भाषा चुनें:</b>",
        "lang_selected": "✅ <b>भाषा हिंदी में बदल दी गई है।</b>",
        "help": "अपना विचार बताओ — मैं उसे वीडियो में बदल दूँगा।",
        
        # Меню и кнопки
        "btn_create_video": "🎬 वीडियो बनाएं",
        "btn_examples": "📘 उदाहरण", 
        "btn_profile": "👤 प्रोफ़ाइल",
        "btn_help": "❓ मदद",
        "btn_language": "🌍 भाषा",
        
        # Ориентация видео
        "choose_orientation": "📐 <b>भविष्य के वीडियो के लिए दिशा चुनें:</b>",
        "orientation_vertical": "📱 खड़ा",
        "orientation_horizontal": "🖥 लेटा",
        "btn_main_menu": "🏠 मुख्य मेनू",
        "btn_cancel": "❌ रद्द करें",
        "orientation_selected": "✅ <b>{orientation} दिशा चुनी गई</b>\n\nअब <b>🎬 वीडियो बनाएं</b> दबाएं और बताएं कि आप क्या फिल्माना चाहते हैं!",
        "orientation_vertical_name": "खड़ी",
        "orientation_horizontal_name": "लेटी",
        
        # Создание видео
        "create_video": "🎬 <b>वीडियो बना रहे हैं</b>\n\n📐 दिशा: <b>{orientation}</b>\n🎞 बचे वीडियो: <b>{videos_left}</b>\n\n✏️ <b>बताएं कि आप क्या फिल्माना चाहते हैं:</b>\nउदाहरण: <code>मछुआरे जाल खींच रहे हैं जिसमें राक्षसी है</code>",
        "video_accepted": "🎬 <b>विवरण स्वीकार किया गया!</b>\n\n📝 <b>विवरण:</b> {description}\n📐 <b>दिशा:</b> {orientation}\n🎞 <b>बचे वीडियो:</b> {videos_left}\n\n⏳ Sora 2 के माध्यम से वीडियो बनाया जा रहा है...\n📨 परिणाम यहाँ भेजा जाएगा!",
        "no_videos_left": "🚫 <b>आपके वीडियो खत्म हो गए!</b>\n\n💳 <b>💰 प्रोफाइल</b> में नया पैकेज खरीदें",
        
        # Примеры
        "examples": "📘 <b>वीडियो आइडिया उदाहरण:</b>\n\n🔹 मछुआरे जाल खींच रहे हैं जिसमें अजीब जीव है\n🔹 मशरूम बीनने वाले पत्तों के नीचे हिलती हुई चीज़ पाते हैं\n🔹 दादी सुबह खिड़की पर कैपिबारा को खाना खिला रही हैं\n🔹 सोवियत कर्मचारी समय कैप्सूल खोल रहे हैं\n🔹 बच्चे दूसरी दुनिया का पोर्टल पाते हैं\n🔹 रात में पुराना भूतिया घर\n\n💡 <b>अब अपना वीडियो बनाएं!</b>",
        
        # Профиль
        "profile": "💰 <b>आपका प्रोफाइल</b>\n\n👤 नाम: <b>{name}</b>\n📦 योजना: <b>{plan}</b>\n🎞 बचे वीडियो: <b>{videos_left}</b>\n📅 पंजीकरण: <b>{date}</b>\n\n🔁 <b>और वीडियो चाहिए?</b>\nपैकेज चुनें:\n🐣 ट्रायल — 3 वीडियो → ₽390\n🎬 बेसिक — 10 वीडियो → ₽990\n🚀 मैक्स — 30 वीडियो → ₽2,190",
        
        # Помощь
        "help_text": "🧭 <b>मदद</b>\n\nअपनी समस्या बताएं, मैं जल्दी मदद करने की कोशिश करूंगा!",
        "support_sent": "✅ संदेश भेजा गया। मैं जल्द से जल्द जवाब देने की कोशिश करूंगा!",
        
        # Кнопки покупки тарифов
        "btn_buy_trial": "🌱 ट्रायल खरीदें (₽390)",
        "btn_buy_basic": "✨ बेसिक खरीदें (₽990)", 
        "btn_buy_maximum": "💎 मैक्स खरीदें (₽2,190)",
        "btn_buy_foreign": "💳 विदेशी कार्ड",
        
        # Сообщения оплаты
        "payment_title": "💳 <b>{tariff} का भुगतान</b>",
        "payment_amount": "💰 राशि: <b>{price} ₽</b>",
        "payment_videos": "🎞 वीडियो: <b>{videos}</b>",
        "payment_activation": "📱 भुगतान के बाद, आपकी योजना स्वचालित रूप से सक्रिय हो जाएगी!",
        "payment_button": "💳 भुगतान करें",
        "payment_error": "❌ भुगतान बनाने में त्रुटि। बाद में पुनः प्रयास करें।",
        "payment_unavailable": "⚠️ भुगतान प्रणाली अस्थायी रूप से अनुपलब्ध है।\nबाद में पुनः प्रयास करें!",
        "foreign_card_title": "💰 <b>अपनी योजना चुनें:</b>",
        "foreign_card_description": "🌍 भुगतान दुनिया भर में काम करता है — Tribute आपकी स्थानीय मुद्रा में कीमत को स्वचालित रूप से परिवर्तित करता है।\n\nभुगतान के बाद, @sora2kudo_bot में आपका खाता स्वचालित रूप से अपडेट हो जाएगा 🎬",
        "foreign_trial": "ट्रायल",
        "foreign_basic": "बेसिक",
        "foreign_premium": "मैक्स",
        "videos": "वीडियो",
        
        # Сообщения для пользователей без тарифа
        "no_tariff_message": "🚀 <b>अभी वायरल वीडियो बनाना शुरू करें!</b>\n\n💎 <b>एक योजना चुनें और SORA 2 तक पहुंच प्राप्त करें:</b>\n🌱 <b>ट्रायल</b> — 3 वीडियो के लिए ₽390\n✨ <b>बेसिक</b> — 10 वीडियो के लिए ₽990\n💎 <b>मैक्स</b> — 30 वीडियो के लिए ₽2,190\n\n🔥 <b>अद्भुत वीडियो बनाएं और अपने दोस्तों और अनुयायियों को खुश करें!</b>",
        "examples_subscription_required": "🔒 <b>उदाहरण केवल सदस्यता के साथ उपलब्ध!</b>\n\n💎 <b>वायरल वीडियो के लिए तैयार विचारों तक पहुंच प्राप्त करें:</b>\n🌱 <b>ट्रायल</b> — 3 वीडियो के लिए ₽390\n✨ <b>बेसिक</b> — 10 वीडियो के लिए ₽990\n💎 <b>मैक्स</b> — 30 वीडियो के लिए ₽2,190\n\n🔥 <b>अद्भुत वीडियो बनाएं और अपने दोस्तों को खुश करें!</b>",
        
        # अतिरिक्त कुंजियां
        "btn_buy_tariff": "💳 योजना खरीदें",
        "tariff_selection": "💳 <b>खरीदने के लिए योजना चुनें:</b>",
        "video_creating": "🎬 <b>वीडियो बनाया जा रहा है...</b>\n\n⏳ Sora 2 के माध्यम से आपके विवरण को संसाधित कर रहे हैं\n🔄 इसमें 2-3 मिनट लग सकते हैं\n\n📹 वीडियो इस चैट में भेजा जाएगा जब तैयार हो जाएगा!",
        "video_error": "❌ <b>वीडियो बनाने में त्रुटि</b>\n\n⚠️ आपके विवरण से वीडियो नहीं बना सके\n🔄 विवरण बदलने का प्रयास करें या सहायता से संपर्क करें\n\n🎞 बचे वीडियो: <b>{videos_left}</b>",
        "video_ready": "🎉 <b>आपका वीडियो तैयार है!</b>\n\n🎬 Sora 2 के माध्यम से वीडियो सफलतापूर्वक बनाया गया\n📹 <b>वीडियो ऊपर चैट में भेजा गया</b>\n🎞 बचे वीडियो: <b>{videos_left}</b>\n\n💡 निर्माण जारी रखने के लिए, एक नया विवरण भेजें!",
        "video_success_title": "🎉 <b>आपका वीडियो तैयार है!</b>",
        "video_success_message": "🎞 <b>बचे वीडियो:</b> {videos_left}\n\n💡 <b>नया वीडियो बनाने के लिए नया अनुरोध भेजें ✍️</b>",
        "btn_change_orientation": "📐 दिशा बदलें",
        
        # Сообщения об ошибках Sora 2
        "sora_error_title": "😔 <b>हम यह वीडियो नहीं बना सकते, यह अनुरोध Sora 2 के नियमों का उल्लंघन करता है</b>",
        "sora_error_rules": "📖 <b>नियमों के बारे में अधिक जानकारी:</b> https://openai.com/policies/usage-policies",
        "sora_error_refund": "💰 <b>वीडियो शेष राशि में वापस कर दिया गया</b>\n🎞 <b>बचे वीडियो:</b> {videos_left}",
        
        # Общие фразы
        "use_buttons": "💡 मेनू बटन का उपयोग करें या वीडियो दिशा चुनें!",
        "error_restart": "❌ त्रुटि। /start आज़माएं",
        "error_getting_data": "❌ डेटा प्राप्त करने में त्रुटि। /start आज़माएं",
    },
}

# Языковые коды и флаги для кнопок
LANGUAGE_BUTTONS = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English", 
    "es": "🇪🇸 Español",
    "ar": "🇸🇦 العربية",
    "hi": "🇮🇳 हिन्दी"
}

def get_text(language: str, key: str, **kwargs) -> str:
    """Получение переведенного текста"""
    if language not in LANG:
        language = "en"
    
    if key not in LANG[language]:
        # Fallback на английский
        if key in LANG["en"]:
            return LANG["en"][key].format(**kwargs)
        return key
    
    return LANG[language][key].format(**kwargs)

def is_rtl_language(language: str) -> bool:
    """Проверка, является ли язык RTL (справа налево)"""
    return language == "ar"

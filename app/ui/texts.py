# app/ui/texts.py
"""Централизованные тексты для интерфейса бота"""

T = {
    "ru": {
        # Выбор языка
        "language.welcome": "🌍 <b>Добро пожаловать в KudoAiBot!</b>\n\nВыберите язык для продолжения:",
        "language.selected": "✅ Язык установлен: Русский\n\nТеперь вы можете пользоваться ботом!",
        
        # Главное меню
        "menu.main": "🏠 <b>Главное меню</b>\n\nВыберите раздел:",
        
        # Главное меню (плоская структура)
        "menu.create_video": "🎬 <b>Создать видео</b>\n\nВыберите режим создания видео:",
        "menu.helper": "🧠 <b>Умный помощник</b>\n\nGPT улучшит ваш промпт и создаст качественное видео:",
        "menu.neurokudo": "🔮 <b>Как у Neurokudo</b>\n\nСпециальный режим с бабушкой и абсурдными ситуациями:",
        "menu.meme": "🤡 <b>Мемный режим</b>\n\nБыстрая генерация смешных сцен:",
        "menu.lego": "🧱 <b>Режим «LEGO мультики» активирован!</b>",
        "menu.photo": "📸 <b>ФОТО</b>\n\nРедактирование фото через Gemini:\n\n• Улучшение качества — 4 монетки за операцию\n• Удаление фона — 4 монетки за операцию\n• Ретушь — 4 монетки за операцию\n• Смена стиля — 4 монетки за операцию",
        "menu.tryon": "👗 <b>ВИРТУАЛЬНАЯ ПРИМЕРОЧНАЯ</b>\n\nИспользуйте Imagen Try-On:\n\n• Imagen Try-On (1 образ) — 6 монеток\n• Imagen Fashion — 10 монеток\n• Imagen Pro (3 образа) — 15 монеток\n\n1) Пришлите фото человека\n2) Затем фото одежды",
        
        # VEO 3 режимы
        "veo3.modes": "🔵 <b>VEO 3</b>\n\nВыберите режим генерации:",
        "veo3.helper": "🤖 <b>Умный помощник</b>\n\nОпишите, что хотите увидеть в видео. Помощник создаст детальный промпт.",
        "veo3.manual": "✋ <b>Ручной режим</b>\n\nВведите готовый детальный промпт для VEO 3.",
        "veo3.meme": "😄 <b>Мемный режим</b>\n\nБыстрая генерация коротких мемных видео!",
        
        # Режимы генерации (общие)
        "mode.helper": "🤖 С помощником",
        "mode.manual": "✋ Вручную", 
        "mode.meme": "😄 Мем",
        
        # LEGO режим
        "lego.single": "🎬 Одна сцена",
        "lego.reportage": "📰 Репортаж",
        "lego.regenerate": "🔄 Перегенерировать",
        "lego.improve": "✨ Улучшить",
        "lego.embed_replica": "📝 Встроить реплику",
        
        # SORA 2 режимы
        "sora2.modes": "🔸 <b>SORA 2</b>\n\nВыберите режим генерации:",
        "sora2.helper": "🤖 <b>Умный помощник</b>\n\nОпишите, что хотите увидеть в видео. Помощник создаст детальный промпт.",
        "sora2.manual": "✋ <b>Ручной режим</b>\n\nВведите готовый детальный промпт для SORA 2.",
        "sora2.meme": "😄 <b>Мемный режим</b>\n\nБыстрая генерация коротких мемных видео!",
        
        # Параметры видео
        "video.orientation": "📐 Выберите ориентацию видео:",
        "video.audio": "🔊 Генерировать аудио?",
        "video.generating": "⏳ Генерирую видео...\nЭто может занять 1-2 минуты.",
        "video.success": "✅ Видео готово!\n\n🔄 Списано: –{cost} монеток",
        "video.error": "❌ Ошибка при генерации видео:\n{error}",
        
        # Мемный режим
        "meme.input": "😄 Введите тему или описание для мема:",
        "meme.generating": "🎬 Генерирую мемное видео...",
        "meme.result": "😄 Мемное видео готово!",
        
        # Помощник
        "helper.input": "🤖 Опишите идею видео:\n\nНапример: 'собака бежит по парку'",
        "helper.thinking": "🤔 Обрабатываю запрос...",
        "helper.prompt": "✨ <b>Улучшенный промпт:</b>\n\n{prompt}\n\n💡 Генерировать видео с этим промптом?",
        
        # Кнопки
        "btn.video": "🎬 ВИДЕО",
        "btn.photo": "📸 ФОТО",
        "btn.tryon": "👗 ПРИМЕРОЧНАЯ",
        "btn.profile": "👤 Профиль",
        
        "btn.sora2": "🔸 SORA 2",
        "btn.veo3": "🔵 VEO 3",
        
        "btn.mode_helper": "🤖 С помощником",
        "btn.mode_manual": "✋ Вручную",
        "btn.mode_meme": "😄 Мем",
        
        "btn.portrait": "📱 Портрет (9:16)",
        "btn.landscape": "🖥️ Альбом (16:9)",
        
        "btn.audio_yes": "🔊 Со звуком",
        "btn.audio_no": "🔇 Без звука",
        
        "btn.generate": "🚀 Генерировать",
        "btn.regenerate": "🔄 Еще раз",
        "btn.to_helper": "🤖 С помощником",
        "btn.back": "⬅️ Назад",
        "btn.home": "🏠 Главное меню",
        
        # Профиль
        "profile.info": "👤 <b>Профиль</b>\n\n💰 Баланс: {balance} монеток\n📊 Тариф: {tariff}",
        
        # Покупка монеток
        "topup.title": "💰 <b>Купить монетки</b>",
        "topup.description": "Выберите пакет пополнения:",
        "topup.success": "✅ <b>Монетки успешно добавлены!</b>\n\n💰 Пополнено: {coins} монеток\n🎁 Бонус: {bonus} монеток\n\n📊 Новый баланс: {balance} монеток",
        
        # Ошибки
        "error.no_balance": "❌ Недостаточно монеток!\n\n⚡ Стоимость: {cost} монеток\n💰 Баланс: {balance} монеток",
        "error.invalid_prompt": "❌ Промпт слишком длинный. Максимум 3000 символов.",
        "error.generation": "❌ Ошибка генерации. Попробуйте еще раз.",
        "error.no_mode_selected": "❌ Сначала выберите режим генерации видео из меню.",
    },
    
    "en": {
        # Language selection
        "language.welcome": "🌍 <b>Welcome to KudoAiBot!</b>\n\nChoose language to continue:",
        "language.selected": "✅ Language set: English\n\nNow you can use the bot!",
        
        # Main menu
        "menu.main": "🏠 <b>Main Menu</b>\n\nChoose section:",
        
        # Sections
        "menu.generate": "🎬 <b>Generate Video</b>\n\nChoose generation mode:",
        "menu.lego": "🧱 <b>LEGO Cartoons mode activated!</b>",
        "menu.photo": "📸 <b>PHOTO</b>\n\nPhoto editing via Gemini:\n\n• Quality enhancement — 4 coins per operation\n• Background removal — 4 coins per operation\n• Retouching — 4 coins per operation\n• Style change — 4 coins per operation",
        "menu.tryon": "👗 <b>VIRTUAL TRY-ON</b>\n\nUse Imagen Try-On:\n\n• Imagen Try-On (1 outfit) — 6 coins\n• Imagen Fashion — 10 coins\n• Imagen Pro (3 outfits) — 15 coins\n\n1) Send person photo\n2) Then clothing photo",
        
        # Generation modes
        "mode.helper": "🤖 With assistant",
        "mode.manual": "✋ Manual", 
        "mode.meme": "😄 Meme",
        
        # LEGO mode
        "lego.single": "🎬 Single scene",
        "lego.reportage": "📰 Reportage",
        "lego.regenerate": "🔄 Regenerate",
        "lego.improve": "✨ Improve",
        "lego.embed_replica": "📝 Embed replica",
        
        # Buttons
        "btn.video": "🎬 VIDEO",
        "btn.photo": "📸 PHOTO", 
        "btn.tryon": "👗 TRY-ON",
        "btn.profile": "👤 Profile",
        "btn.back": "⬅️ Back",
        "btn.home": "🏠 Main Menu"
    },
    
    "es": {
        # Language selection
        "language.welcome": "🌍 <b>¡Bienvenido a KudoAiBot!</b>\n\nElige idioma para continuar:",
        "language.selected": "✅ Idioma establecido: Español\n\n¡Ahora puedes usar el bot!",
        
        # Main menu
        "menu.main": "🏠 <b>Menú Principal</b>\n\nElige sección:",
        
        # Sections
        "menu.generate": "🎬 <b>Generar Video</b>\n\nElige modo de generación:",
        "menu.lego": "🧱 <b>¡Modo «LEGO Cartoons» activado!</b>",
        "menu.photo": "📸 <b>FOTO</b>\n\nEdición de fotos vía Gemini:\n\n• Mejora de calidad — 4 monedas por operación\n• Eliminación de fondo — 4 monedas por operación\n• Retoque — 4 monedas por operación\n• Cambio de estilo — 4 monedas por operación",
        "menu.tryon": "👗 <b>PROBADOR VIRTUAL</b>\n\nUsa Imagen Try-On:\n\n• Imagen Try-On (1 outfit) — 6 monedas\n• Imagen Fashion — 10 monedas\n• Imagen Pro (3 outfits) — 15 monedas\n\n1) Envía foto de persona\n2) Luego foto de ropa",
        
        # Generation modes
        "mode.helper": "🤖 Con asistente",
        "mode.manual": "✋ Manual", 
        "mode.meme": "😄 Meme",
        
        # LEGO mode
        "lego.single": "🎬 Una escena",
        "lego.reportage": "📰 Reportaje",
        "lego.regenerate": "🔄 Regenerar",
        "lego.improve": "✨ Mejorar",
        "lego.embed_replica": "📝 Insertar réplica",
        
        # Buttons
        "btn.video": "🎬 VIDEO",
        "btn.photo": "📸 FOTO",
        "btn.tryon": "👗 PROBADOR", 
        "btn.profile": "👤 Perfil",
        "btn.back": "⬅️ Atrás",
        "btn.home": "🏠 Menú Principal"
    },
    
    "ar": {
        # Language selection
        "language.welcome": "🌍 <b>مرحباً بك في KudoAiBot!</b>\n\nاختر اللغة للمتابعة:",
        "language.selected": "✅ تم تعيين اللغة: العربية\n\nيمكنك الآن استخدام البوت!",
        
        # Main menu
        "menu.main": "🏠 <b>القائمة الرئيسية</b>\n\nاختر القسم:",
        
        # Sections
        "menu.generate": "🎬 <b>إنشاء فيديو</b>\n\nاختر وضع الإنشاء:",
        "menu.lego": "🧱 <b>وضع «LEGO Cartoons» مفعل!</b>",
        "menu.photo": "📸 <b>صورة</b>\n\nتعديل الصور عبر Gemini:\n\n• تحسين الجودة — 4 عملات لكل عملية\n• إزالة الخلفية — 4 عملات لكل عملية\n• التعديل — 4 عملات لكل عملية\n• تغيير الأسلوب — 4 عملات لكل عملية",
        "menu.tryon": "👗 <b>غرفة القياس الافتراضية</b>\n\nاستخدم Imagen Try-On:\n\n• Imagen Try-On (1 زي) — 6 عملات\n• Imagen Fashion — 10 عملات\n• Imagen Pro (3 أزياء) — 15 عملة\n\n1) أرسل صورة الشخص\n2) ثم صورة الملابس",
        
        # Generation modes
        "mode.helper": "🤖 مع المساعد",
        "mode.manual": "✋ يدوي", 
        "mode.meme": "😄 ميم",
        
        # LEGO mode
        "lego.single": "🎬 مشهد واحد",
        "lego.reportage": "📰 تقرير",
        "lego.regenerate": "🔄 إعادة إنشاء",
        "lego.improve": "✨ تحسين",
        "lego.embed_replica": "📝 إدراج نسخة",
        
        # Buttons
        "btn.video": "🎬 فيديو",
        "btn.photo": "📸 صورة",
        "btn.tryon": "👗 غرفة القياس",
        "btn.profile": "👤 الملف الشخصي",
        "btn.back": "⬅️ رجوع",
        "btn.home": "🏠 القائمة الرئيسية"
    },
    
    "hi": {
        # Language selection
        "language.welcome": "🌍 <b>KudoAiBot में आपका स्वागत है!</b>\n\nजारी रखने के लिए भाषा चुनें:",
        "language.selected": "✅ भाषा सेट: हिंदी\n\nअब आप बॉट का उपयोग कर सकते हैं!",
        
        # Main menu
        "menu.main": "🏠 <b>मुख्य मेनू</b>\n\nअनुभाग चुनें:",
        
        # Sections
        "menu.generate": "🎬 <b>वीडियो जेनरेट करें</b>\n\nजेनरेशन मोड चुनें:",
        "menu.lego": "🧱 <b>LEGO Cartoons मोड सक्रिय!</b>",
        "menu.photo": "📸 <b>फोटो</b>\n\nGemini के माध्यम से फोटो संपादन:\n\n• गुणवत्ता सुधार — 4 सिक्के प्रति ऑपरेशन\n• पृष्ठभूमि हटाना — 4 सिक्के प्रति ऑपरेशन\n• रिटचिंग — 4 सिक्के प्रति ऑपरेशन\n• स्टाइल बदलना — 4 सिक्के प्रति ऑपरेशन",
        "menu.tryon": "👗 <b>वर्चुअल ट्राई-ऑन</b>\n\nImagen Try-On का उपयोग करें:\n\n• Imagen Try-On (1 आउटफिट) — 6 सिक्के\n• Imagen Fashion — 10 सिक्के\n• Imagen Pro (3 आउटफिट) — 15 सिक्के\n\n1) व्यक्ति की फोटो भेजें\n2) फिर कपड़े की फोटो",
        
        # Generation modes
        "mode.helper": "🤖 सहायक के साथ",
        "mode.manual": "✋ मैनुअल", 
        "mode.meme": "😄 मीम",
        
        # LEGO mode
        "lego.single": "🎬 एक दृश्य",
        "lego.reportage": "📰 रिपोर्ट",
        "lego.regenerate": "🔄 पुनः जेनरेट करें",
        "lego.improve": "✨ सुधारें",
        "lego.embed_replica": "📝 रेप्लिका एम्बेड करें",
        
        # Buttons
        "btn.video": "🎬 वीडियो",
        "btn.photo": "📸 फोटो",
        "btn.tryon": "👗 ट्राई-ऑन",
        "btn.profile": "👤 प्रोफाइल",
        "btn.back": "⬅️ वापस",
        "btn.home": "🏠 मुख्य मेनू"
    }
}

def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить локализованный текст"""
    text = T.get(lang, {}).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


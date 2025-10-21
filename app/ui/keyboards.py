# app/ui/keyboards.py
"""Клавиатуры для бота"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callbacks import Cb, Actions
from .texts import t

__all__ = [
    'build_language_menu',
    'build_main_menu',
    'build_video_menu',
    'build_veo3_modes',
    'build_sora2_modes',
    'build_orientation_menu',
    'build_audio_menu',
    'build_video_result_menu',
    'build_confirm_generate',
    'build_keyboard',
    'tariff_selection',
    'topup_packs_menu',
    'build_profile_menu',
    'build_tariffs_menu',
    'build_help_menu',
    'btn'
]

def btn(text: str, action: str, id: str = None, extra: str = None) -> InlineKeyboardButton:
    """Создать кнопку с callback данными"""
    cb = Cb(action=action, id=id, extra=extra)
    return InlineKeyboardButton(text=text, callback_data=cb.pack())

def build_language_menu() -> InlineKeyboardMarkup:
    """Меню выбора языка"""
    keyboard = [
        [btn("🇷🇺 Русский", "set_language", extra="ru")],
        [btn("🇺🇸 English", "set_language", extra="en")],
        [btn("🇪🇸 Español", "set_language", extra="es")],
        [btn("🇸🇦 العربية", "set_language", extra="ar")],
        [btn("🇮🇳 हिंदी", "set_language", extra="hi")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню - финальная версия"""
    keyboard = [
        [btn("🎬 Создать видео", "menu_video")],
        [btn("🪄 Редактировать фото", "menu_photo")],
        [btn("👗 Примерочная", "menu_tryon")],
        [btn("💳 Подписка и монетки", "menu_tariffs")],
        [btn("👤 Мой профиль", "menu_profile")],
        [btn("ℹ️ Как это работает", "menu_help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_video_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню выбора платформы видео"""
    from app.core.features import FeatureFlags
    
    keyboard = []
    
    # VEO 3 платформа (если доступна)
    if FeatureFlags.has_veo3():
        keyboard.append([btn("🔵 VEO 3", Actions.VIDEO_VEO3)])
    else:
        keyboard.append([btn("⚠️ VEO 3 недоступен (нет GCP ключа)", "disabled_veo3")])
    
    # SORA 2 платформа (если доступна)
    if FeatureFlags.has_sora2():
        keyboard.append([btn("🔸 SORA 2", Actions.VIDEO_SORA2)])
    else:
        keyboard.append([btn("⚠️ SORA 2 недоступен (нет OpenAI ключа)", "disabled_sora2")])
    
    keyboard.append([btn(t("btn.back", lang), Actions.HOME)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_veo3_modes(lang: str = "ru") -> InlineKeyboardMarkup:
    """Режимы генерации VEO 3 (как в babka-bot-clean)"""
    from app.core.features import FeatureFlags
    
    keyboard = []
    
    # GPT режимы (только если OpenAI доступен)
    if FeatureFlags.has_gpt_helper():
        keyboard.append([btn(t("mode.helper", lang), Actions.MODE_HELPER)])
        keyboard.append([btn(t("mode.meme", lang), Actions.MODE_MEME)])
    
    # Ручной режим (всегда доступен)
    keyboard.append([btn(t("mode.manual", lang), Actions.MODE_MANUAL)])
    
    keyboard.append([btn(t("btn.back", lang), Actions.HOME)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_sora2_modes(lang: str = "ru") -> InlineKeyboardMarkup:
    """Режимы генерации SORA 2 (как в babka-bot-clean)"""
    from app.core.features import FeatureFlags
    
    keyboard = []
    
    # GPT режимы (только если OpenAI доступен)
    if FeatureFlags.has_gpt_helper():
        keyboard.append([btn(t("mode.helper", lang), Actions.MODE_HELPER)])
        keyboard.append([btn(t("mode.meme", lang), Actions.MODE_MEME)])
    
    # Ручной режим (всегда доступен)
    keyboard.append([btn(t("mode.manual", lang), Actions.MODE_MANUAL)])
    
    keyboard.append([btn(t("btn.back", lang), Actions.HOME)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_orientation_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор ориентации"""
    keyboard = [
        [btn(t("btn.portrait", lang), Actions.ORIENTATION_PORTRAIT)],
        [btn(t("btn.landscape", lang), Actions.ORIENTATION_LANDSCAPE)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_audio_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор аудио"""
    keyboard = [
        [btn(t("btn.audio_yes", lang), Actions.AUDIO_YES)],
        [btn(t("btn.audio_no", lang), Actions.AUDIO_NO)],
        [btn(t("btn.back", lang), Actions.BACK)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_video_result_menu(lang: str = "ru", with_helper: bool = True) -> InlineKeyboardMarkup:
    """Меню после генерации видео"""
    keyboard = [
        [btn(t("btn.regenerate", lang), Actions.VIDEO_REGENERATE)],
    ]
    if with_helper:
        keyboard.append([btn(t("btn.to_helper", lang), Actions.VIDEO_TO_HELPER)])
    keyboard.append([btn(t("btn.home", lang), Actions.HOME)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_confirm_generate(lang: str = "ru", back_action: str = Actions.BACK) -> InlineKeyboardMarkup:
    """Подтверждение генерации"""
    keyboard = [
        [btn(t("btn.generate", lang), Actions.NAV, "generate")],
        [btn(t("btn.back", lang), back_action)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def tariff_selection(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора тарифов для покупки"""
    from app.config.pricing import TARIFFS
    
    keyboard = []
    
    # Добавляем кнопки для каждого тарифа
    for tariff_key, tariff_info in TARIFFS.items():
        button_text = f"{tariff_info.icon} {tariff_info.title} — {tariff_info.price_rub} ₽"
        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"buy_tariff_{tariff_key}"
            )
        ])
    
    # Кнопка "Купить монетки"
    keyboard.append([
        InlineKeyboardButton(
            text="💰 Купить монетки",
            callback_data=Actions.PAYMENT_TOPUP
        )
    ])
    
    # Кнопка "Главное меню"
    keyboard.append([
        InlineKeyboardButton(
            text=t("btn.home", lang),
            callback_data=Actions.HOME
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def topup_packs_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора пакетов пополнения"""
    from app.config.pricing import TOPUP_PACKS
    
    keyboard = []
    
    # Добавляем кнопки для каждого пакета
    for pack in TOPUP_PACKS:
        total_coins = pack.coins + pack.bonus_coins
        if pack.bonus_coins > 0:
            button_text = f"💰 {total_coins} монеток ({pack.coins}+{pack.bonus_coins} бонус) — {pack.price_rub} ₽"
        else:
            button_text = f"💰 {pack.coins} монеток — {pack.price_rub} ₽"
        
        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"buy_topup_{pack.coins}"
            )
        ])
    
    # Кнопки навигации
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ К тарифам",
            callback_data=Actions.MENU_PROFILE
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            text=t("btn.home", lang),
            callback_data=Actions.HOME
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_keyboard(screen_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Универсальный билдер клавиатуры"""
    if screen_id == "main":
        return build_main_menu(lang)
    elif screen_id == "video":
        return build_video_menu(lang)
    elif screen_id == "veo3_modes":
        return build_veo3_modes(lang)
    elif screen_id == "sora2_modes":
        return build_sora2_modes(lang)
    elif screen_id == "orientation":
        return build_orientation_menu(lang)
    elif screen_id == "audio":
        return build_audio_menu(lang)
    else:
        return build_main_menu(lang)

def build_profile_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню профиля - финальная версия"""
    keyboard = [
        [btn("💳 Пополнить баланс", "show_topup")],
        [btn("💸 Стоимость моделей", "models_cost")],
        [btn("⬅️ Назад", "home")],
        [btn("🏠 Главное меню", "home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_tariffs_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню подписки и монеток - финальная версия"""
    keyboard = [
        [btn("🎟 Подписка (на 30 дней)", "subscriptions")],
        [btn("🟣 Монетки навсегда", "permanent_coins")],
        [btn("💸 Стоимость моделей", "models_cost")],
        [btn("⬅️ Назад", "home")],
        [btn("🏠 Главное меню", "home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_help_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню помощи - финальная версия"""
    keyboard = [
        [btn("⬅️ Назад", "home")],
        [btn("🏠 Главное меню", "home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


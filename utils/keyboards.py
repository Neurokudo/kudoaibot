"""
🌍 Клавиатуры с поддержкой мультиязычности для SORA 2
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from translations import get_text, LANGUAGE_BUTTONS

def main_menu(language: str = "en") -> InlineKeyboardMarkup:
    """Главное меню (inline) с учетом языка"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_create_video"),
                callback_data="menu_create_video"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_examples"),
                callback_data="menu_examples"
            ),
            InlineKeyboardButton(
                text=get_text(language, "btn_profile"),
                callback_data="menu_profile"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_help"),
                callback_data="menu_help"
            ),
            InlineKeyboardButton(
                text=get_text(language, "btn_language"),
                callback_data="menu_language"
            )
        ]
    ])
    return markup

def language_selection() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LANGUAGE_BUTTONS["ru"], callback_data="lang_ru"),
            InlineKeyboardButton(text=LANGUAGE_BUTTONS["en"], callback_data="lang_en")
        ],
        [
            InlineKeyboardButton(text=LANGUAGE_BUTTONS["es"], callback_data="lang_es"),
            InlineKeyboardButton(text=LANGUAGE_BUTTONS["ar"], callback_data="lang_ar")
        ],
        [
            InlineKeyboardButton(text=LANGUAGE_BUTTONS["hi"], callback_data="lang_hi")
        ]
    ])
    return markup

def orientation_menu(language: str = "en") -> InlineKeyboardMarkup:
    """Меню выбора ориентации видео"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(language, "orientation_vertical"), 
                callback_data="orientation_vertical"
            ),
            InlineKeyboardButton(
                text=get_text(language, "orientation_horizontal"), 
                callback_data="orientation_horizontal"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_main_menu"),
                callback_data="main_menu"
            )
        ]
    ])
    return markup

def video_confirmation_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания видео"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_create_confirm"),
                callback_data="confirm_create_video"
            ),
            InlineKeyboardButton(
                text=get_text(language, "btn_edit_request"),
                callback_data="edit_video_request"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_cancel_request"),
                callback_data="cancel_video_request"
            )
        ]
    ])
    return markup

def video_ready_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура после создания видео"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_main_menu"),
                callback_data="main_menu"
            ),
            InlineKeyboardButton(
                text=get_text(language, "btn_examples"),
                callback_data="menu_examples"
            )
        ]
    ])
    return markup

def support_sent_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура после отправки сообщения в поддержку"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_create_video"),
                callback_data="menu_create_video"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_main_menu"),
                callback_data="main_menu"
            )
        ]
    ])
    return markup

def help_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура для помощи с кнопкой отмены"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, "btn_cancel"),
            callback_data="cancel_help"
        )],
        [InlineKeyboardButton(
            text=get_text(language, "btn_main_menu"),
            callback_data="main_menu"
        )]
    ])
    return markup

def tariff_selection(language: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура выбора тарифов для покупки"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_buy_trial"), 
                callback_data="buy_trial"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_buy_basic"), 
                callback_data="buy_basic"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_buy_maximum"), 
                callback_data="buy_maximum"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_buy_foreign"), 
                callback_data="buy_foreign"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "btn_main_menu"),
                callback_data="main_menu"
            )
        ]
    ])
    return markup
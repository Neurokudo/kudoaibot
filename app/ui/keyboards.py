# app/ui/keyboards.py
"""Клавиатуры для бота"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callbacks import Cb, Actions
from .texts import t

def btn(text: str, action: str, id: str = None, extra: str = None) -> InlineKeyboardButton:
    """Создать кнопку с callback данными"""
    cb = Cb(action=action, id=id, extra=extra)
    return InlineKeyboardButton(text=text, callback_data=cb.pack())

def build_main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню"""
    keyboard = [
        [btn(t("btn.video", lang), Actions.MENU_VIDEO)],
        [btn(t("btn.photo", lang), Actions.MENU_PHOTO)],
        [btn(t("btn.tryon", lang), Actions.MENU_TRYON)],
        [btn(t("btn.profile", lang), Actions.MENU_PROFILE)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_video_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню выбора видео модели"""
    keyboard = [
        [btn(t("btn.sora2", lang), Actions.VIDEO_SORA2)],
        [btn(t("btn.veo3", lang), Actions.VIDEO_VEO3)],
        [btn(t("btn.back", lang), Actions.HOME)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_veo3_modes(lang: str = "ru") -> InlineKeyboardMarkup:
    """Режимы генерации VEO 3"""
    keyboard = [
        [btn(t("btn.mode_helper", lang), Actions.MODE_HELPER)],
        [btn(t("btn.mode_manual", lang), Actions.MODE_MANUAL)],
        [btn(t("btn.mode_meme", lang), Actions.MODE_MEME)],
        [btn(t("btn.back", lang), Actions.MENU_VIDEO)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_sora2_modes(lang: str = "ru") -> InlineKeyboardMarkup:
    """Режимы генерации SORA 2"""
    keyboard = [
        [btn(t("btn.mode_helper", lang), Actions.MODE_HELPER, "sora2")],
        [btn(t("btn.mode_manual", lang), Actions.MODE_MANUAL, "sora2")],
        [btn(t("btn.mode_meme", lang), Actions.MODE_MEME, "sora2")],
        [btn(t("btn.back", lang), Actions.MENU_VIDEO)],
    ]
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


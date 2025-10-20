# app/handlers/callbacks.py
"""Обработчики callback кнопок"""

import logging
from aiogram import F
from aiogram.types import CallbackQuery

from app.db import users
from app.services import billing
from app.ui import Actions, t
from app.ui.keyboards import build_main_menu, tariff_selection, topup_packs_menu
from app.core.bot import dp
from .commands import ensure_user_exists, get_user_language, get_user_data
from .video_handlers import (
    handle_video_menu,
    handle_veo3_menu,
    handle_sora2_menu,
    handle_mode_helper,
    handle_mode_manual,
    handle_mode_meme,
    handle_orientation_choice,
    handle_audio_choice,
    handle_video_regenerate,
    handle_video_to_helper
)

log = logging.getLogger("kudoaibot")

# === НАВИГАЦИЯ ===

@dp.callback_query(F.data == Actions.HOME)
async def callback_home(callback: CallbackQuery):
    """Главное меню"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_language = await get_user_language(callback.from_user.id)
    
    user_id = callback.from_user.id
    user_data = await get_user_data(user_id)
    name = callback.from_user.first_name or "друг"
    
    welcome_text = f"👋 {name}\n\n"
    welcome_text += "💰 Баланс: {videos_left} монеток\n".format(**user_data)
    welcome_text += "📊 Тариф: {subscription_type}\n\n".format(**user_data)
    welcome_text += "Выбери раздел:"
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=build_main_menu(user_language)
    )

# === РАЗДЕЛЫ ===

@dp.callback_query(F.data == Actions.MENU_VIDEO)
async def callback_video(callback: CallbackQuery):
    """Раздел ВИДЕО"""
    await callback.answer()
    await handle_video_menu(callback)

@dp.callback_query(F.data == Actions.VIDEO_VEO3)
async def callback_veo3(callback: CallbackQuery):
    """VEO 3 меню"""
    await callback.answer()
    await handle_veo3_menu(callback)

@dp.callback_query(F.data == Actions.VIDEO_SORA2)
async def callback_sora2(callback: CallbackQuery):
    """SORA 2 меню"""
    await callback.answer()
    await handle_sora2_menu(callback)

@dp.callback_query(F.data == Actions.MENU_PHOTO)
async def callback_photo(callback: CallbackQuery):
    """Раздел ФОТО"""
    await callback.answer()
    await callback.message.edit_text(
        t("menu.photo"),
        reply_markup=build_main_menu()
    )

@dp.callback_query(F.data == Actions.MENU_TRYON)
async def callback_tryon(callback: CallbackQuery):
    """Раздел ПРИМЕРОЧНАЯ"""
    await callback.answer()
    await callback.message.edit_text(
        t("menu.tryon"),
        reply_markup=build_main_menu()
    )

@dp.callback_query(F.data == Actions.MENU_PROFILE)
async def callback_profile(callback: CallbackQuery):
    """Профиль"""
    await callback.answer()
    await ensure_user_exists(callback.message)
    user_id = callback.from_user.id
    user_language = await get_user_language(user_id)
    
    user_data = await get_user_data(user_id)
    name = callback.from_user.first_name or "Пользователь"
    
    user = await users.get_user(user_id)
    reg_date = user.get('created_at', 'Неизвестно') if user else 'Неизвестно'
    
    profile_text = f"👤 <b>Профиль</b>\n\n"
    profile_text += f"Имя: {name}\n"
    profile_text += f"💰 Баланс: {user_data['videos_left']} монеток\n"
    profile_text += f"📊 Тариф: {user_data['subscription_type']}\n"
    profile_text += f"📅 Регистрация: {reg_date}\n"
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=tariff_selection(user_language)
    )

# === РЕЖИМЫ ГЕНЕРАЦИИ ===

@dp.callback_query(F.data == Actions.MODE_HELPER)
async def callback_mode_helper(callback: CallbackQuery):
    """Режим умного помощника"""
    await callback.answer()
    await handle_mode_helper(callback)

@dp.callback_query(F.data == Actions.MODE_MANUAL)
async def callback_mode_manual(callback: CallbackQuery):
    """Ручной режим"""
    await callback.answer()
    await handle_mode_manual(callback)

@dp.callback_query(F.data == Actions.MODE_MEME)
async def callback_mode_meme(callback: CallbackQuery):
    """Мемный режим"""
    await callback.answer()
    await handle_mode_meme(callback)

# === ПАРАМЕТРЫ ВИДЕО ===

@dp.callback_query(F.data == Actions.ORIENTATION_PORTRAIT)
async def callback_orientation_portrait(callback: CallbackQuery):
    """Портретная ориентация"""
    await callback.answer()
    await handle_orientation_choice(callback)

@dp.callback_query(F.data == Actions.ORIENTATION_LANDSCAPE)
async def callback_orientation_landscape(callback: CallbackQuery):
    """Ландшафтная ориентация"""
    await callback.answer()
    await handle_orientation_choice(callback)

@dp.callback_query(F.data == Actions.AUDIO_YES)
async def callback_audio_yes(callback: CallbackQuery):
    """Со звуком"""
    await callback.answer()
    await handle_audio_choice(callback)

@dp.callback_query(F.data == Actions.AUDIO_NO)
async def callback_audio_no(callback: CallbackQuery):
    """Без звука"""
    await callback.answer()
    await handle_audio_choice(callback)

# === ПОСЛЕ ГЕНЕРАЦИИ ===

@dp.callback_query(F.data == Actions.VIDEO_REGENERATE)
async def callback_video_regenerate(callback: CallbackQuery):
    """Повторная генерация"""
    await callback.answer()
    await handle_video_regenerate(callback)

@dp.callback_query(F.data == Actions.VIDEO_TO_HELPER)
async def callback_video_to_helper(callback: CallbackQuery):
    """Переход к помощнику"""
    await callback.answer()
    await handle_video_to_helper(callback)

# === ПОКУПКА МОНЕТОК ===

@dp.callback_query(F.data == Actions.PAYMENT_TOPUP)
async def callback_show_topup(callback: CallbackQuery):
    """Показать пакеты пополнения монеток"""
    await callback.answer()
    
    from app.config.pricing import format_topup_packs_text
    
    topup_text = "💰 <b>Купить монетки</b>\n\n"
    topup_text += format_topup_packs_text()
    topup_text += "\n\n💡 Выберите пакет:"
    
    await callback.message.edit_text(
        topup_text,
        reply_markup=topup_packs_menu()
    )


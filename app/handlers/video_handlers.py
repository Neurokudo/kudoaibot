# app/handlers/video_handlers.py
"""Обработчики для генерации видео"""

import os
import logging
from aiogram import types
from aiogram.types import Message, CallbackQuery, FSInputFile

from app.ui import parse_cb, Actions, t
from app.ui.keyboards import (
    build_video_menu,
    build_veo3_modes,
    build_sora2_modes,
    build_orientation_menu,
    build_audio_menu,
    build_video_result_menu,
    build_main_menu
)
from app.handlers.states import get_user_state, clear_user_state
from app.services.ai_helper import improve_prompt_async
from app.services.clients import generate_video_veo3_async, generate_video_sora2_async
from app.services import billing
from app.config.pricing import get_feature_cost

log = logging.getLogger("video_handlers")

MAX_PROMPT_LENGTH = 3000

async def handle_video_menu(callback: CallbackQuery):
    """Меню выбора видео модели"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    state.current_screen = "video"
    
    await callback.message.edit_text(
        t("menu.video"),
        reply_markup=build_video_menu()
    )

async def handle_generate_menu(callback: CallbackQuery):
    """Меню режимов генерации VEO 3 (как в babka-bot-clean)"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    state.video_model = "veo3"  # По умолчанию VEO 3
    state.current_screen = "generate_modes"
    
    await callback.message.edit_text(
        t("menu.generate"),
        reply_markup=build_generate_menu()
    )

async def handle_lego_menu(callback: CallbackQuery):
    """Меню LEGO мультиков"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    state.current_screen = "lego_menu"
    
    await callback.message.edit_text(
        t("menu.lego"),
        reply_markup=build_lego_menu()
    )

async def handle_mode_helper(callback: CallbackQuery):
    """Активация режима умного помощника"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    
    # Определяем модель из callback.data
    cb = parse_cb(callback.data)
    if cb.id == "sora2":
        state.video_model = "sora2"
        text_key = "sora2.helper"
    else:
        state.video_model = "veo3"
        text_key = "veo3.helper"
    
    state.video_mode = "helper"
    state.waiting_for = "prompt_input"
    
    await callback.message.edit_text(
        t("helper.input"),
        reply_markup=build_main_menu()
    )

async def handle_mode_manual(callback: CallbackQuery):
    """Активация ручного режима"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    
    # Определяем модель из callback.data
    cb = parse_cb(callback.data)
    if cb.id == "sora2":
        state.video_model = "sora2"
        text_key = "sora2.manual"
    else:
        state.video_model = "veo3"
        text_key = "veo3.manual"
    
    state.video_mode = "manual"
    state.waiting_for = "prompt_input"
    
    await callback.message.edit_text(
        t(text_key),
        reply_markup=build_main_menu()
    )

async def handle_mode_meme(callback: CallbackQuery):
    """Активация мемного режима"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    
    # Определяем модель из callback.data
    cb = parse_cb(callback.data)
    if cb.id == "sora2":
        state.video_model = "sora2"
        text_key = "sora2.meme"
    else:
        state.video_model = "veo3"
        text_key = "veo3.meme"
    
    state.video_mode = "meme"
    state.waiting_for = "prompt_input"
    
    await callback.message.edit_text(
        t("meme.input"),
        reply_markup=build_main_menu()
    )

async def handle_text_input(message: Message, custom_prompt: str = None):
    """Обработка текстового ввода от пользователя"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    log.info(f"📝 handle_text_input: user_id={user_id}, waiting_for={getattr(state, 'waiting_for', 'None')}, awaiting_prompt={getattr(state, 'awaiting_prompt', 'None')}")
    
    if not state.waiting_for and not state.awaiting_prompt and not custom_prompt:
        log.info(f"❌ handle_text_input: Не ожидаем ввод от пользователя {user_id}")
        return
    
    if state.waiting_for == "prompt_input" or state.awaiting_prompt or custom_prompt:
        prompt = custom_prompt or message.text.strip()
        await process_prompt_input(message, state, prompt)
    
    state.waiting_for = None
    state.awaiting_prompt = False

async def process_prompt_input(message: Message, state, prompt: str):
    """Обработка промпта от пользователя"""
    user_id = message.from_user.id
    
    log.info(f"🔍 process_prompt_input: user_id={user_id}, mode={getattr(state, 'video_mode', 'None')}, prompt='{prompt[:50]}...'")
    
    if len(prompt) > MAX_PROMPT_LENGTH:
        await message.answer(
            t("error.invalid_prompt"),
            reply_markup=build_main_menu()
        )
        return
    
    # В зависимости от режима обрабатываем промпт
    if state.video_mode == "helper":
        # Улучшаем промпт через GPT
        status_msg = await message.answer(t("helper.thinking"))
        
        try:
            improved_prompt = await improve_prompt_async(prompt, mode="helper")
            state.last_prompt = improved_prompt
            
            await status_msg.delete()
            
            # Запрашиваем параметры видео
            await ask_orientation(message, state, improved_prompt)
            
        except Exception as e:
            log.error(f"Ошибка улучшения промпта: {e}")
            await status_msg.edit_text(
                t("error.generation"),
                reply_markup=build_main_menu()
            )
    
    elif state.video_mode == "meme":
        # Генерируем мемный промпт
        status_msg = await message.answer(t("meme.generating"))
        
        try:
            meme_prompt = await improve_prompt_async(prompt, mode="meme")
            state.last_prompt = meme_prompt
            
            # Для мемов используем быстрые настройки: 6 сек, 9:16, без звука
            state.video_params = {
                "duration": 6,
                "aspect_ratio": "9:16",
                "with_audio": False
            }
            
            await status_msg.delete()
            await generate_video(message, state)
            
        except Exception as e:
            log.error(f"Ошибка генерации мема: {e}")
            await status_msg.edit_text(
                t("error.generation"),
                reply_markup=build_main_menu()
            )
    
    elif state.video_mode == "manual":
        # Используем промпт как есть и сразу генерируем
        state.last_prompt = prompt
        await generate_video(message, state)
    
    else:
        # Если режим не установлен, показываем меню выбора
        log.warning(f"⚠️ process_prompt_input: video_mode не установлен для пользователя {user_id}")
        await message.answer(
            t("error.no_mode_selected"),
            reply_markup=build_main_menu()
        )
        clear_user_state(user_id)

async def ask_orientation(message: Message, state, prompt: str):
    """Запрос ориентации видео"""
    state.waiting_for = "orientation"
    
    await message.answer(
        t("video.orientation"),
        reply_markup=build_orientation_menu()
    )

async def handle_orientation_choice(callback: CallbackQuery):
    """Обработка выбора ориентации"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    
    # Инициализируем video_params если её нет
    if not hasattr(state, 'video_params') or state.video_params is None:
        state.video_params = {}
    
    cb = parse_cb(callback.data)
    
    if cb.action == Actions.ORIENTATION_PORTRAIT:
        state.video_params["aspect_ratio"] = "9:16"
    else:  # ORIENTATION_LANDSCAPE
        state.video_params["aspect_ratio"] = "16:9"
    
    # Запрашиваем настройки аудио
    await callback.message.edit_text(
        t("video.audio"),
        reply_markup=build_audio_menu()
    )

async def handle_audio_choice(callback: CallbackQuery):
    """Обработка выбора аудио"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    
    cb = parse_cb(callback.data)
    
    if cb.action == Actions.AUDIO_YES:
        state.video_params["with_audio"] = True
    else:  # AUDIO_NO
        state.video_params["with_audio"] = False
    
    # По умолчанию 8 секунд
    state.video_params["duration"] = 8
    
    # Устанавливаем состояние ожидания промпта
    state.awaiting_prompt = True
    
    # Запрашиваем промпт
    await callback.message.edit_text(
        "🎬 **Отлично! Теперь опишите сцену для видео:**\n\n"
        "Пример: \"Бабушка кормит кур во дворе\"\n"
        "Или: \"Кот играет с мячиком в гостиной\""
    )

async def generate_video(message: Message, state):
    """Генерация видео"""
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    
    log.info(f"🎬 generate_video: user_id={user_id}, model={getattr(state, 'video_model', 'None')}")
    
    # Проверяем доступ
    feature_name = "video_8s_mute" if not state.video_params.get("with_audio", False) else "video_8s_audio"
    access = await billing.check_access(user_id, feature_name)
    
    if not access['access']:
        await message.answer(
            t("error.no_balance", cost=access.get('cost', 0), balance=access.get('balance', 0)),
            reply_markup=build_main_menu()
        )
        clear_user_state(user_id)
        return
    
    # Уведомляем о начале генерации
    status_msg = await message.answer(t("video.generating"))
    
    try:
        # Списываем монетки
        cost = get_feature_cost(feature_name)
        deduct_result = await billing.deduct_coins_for_feature(user_id, feature_name)
        
        if not deduct_result['success']:
            await status_msg.edit_text(
                deduct_result['message'],
                reply_markup=build_main_menu()
            )
            clear_user_state(user_id)
            return
        
        # Показываем информацию о списании
        deduction_info = (
            f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
            f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
        )
        
        # Генерируем видео
        if state.video_model == "sora2":
            # SORA 2 использует асинхронную генерацию через callback
            from app.services.clients.sora_client import create_sora_task
            
            task_id, task_status = await create_sora_task(
                prompt=state.last_prompt,
                aspect_ratio=state.video_params.get("aspect_ratio", "9:16"),
                duration=state.video_params.get("duration", 5),
                user_id=user_id
            )
            
            if task_status == "success":
                # Задача создана успешно
                await status_msg.edit_text(
                    f"✨ <b>Ваше видео создается!</b>\n\n"
                    f"{deduction_info}"
                    f"🎬 <b>Описание:</b> {state.last_prompt}\n\n"
                    f"🆔 <b>ID задачи:</b> <code>{task_id}</code>\n\n"
                    f"⏳ <b>Ожидайте уведомление когда видео будет готово</b>\n\n"
                    f"📼 <b>Видео будет отправлено в этот чат автоматически</b>",
                    reply_markup=build_main_menu()
                )
                clear_user_state(user_id)
                return
            elif task_status == "demo_mode":
                await status_msg.edit_text(
                    "🎬 <b>Демо режим SORA 2</b>\n\n"
                    "⚠️ OpenAI SORA 2 API не настроен\n"
                    "🔄 Добавьте OPENAI_API_KEY в переменные окружения\n\n"
                    "Используйте VEO 3 для реальной генерации!",
                    reply_markup=build_main_menu()
                )
                clear_user_state(user_id)
                return
            else:
                # Ошибка создания задачи
                result = {"error": f"Failed to create SORA 2 task: {task_status}"}
        else:  # veo3 - асинхронная генерация
            from app.services.clients.veo_client import create_veo3_task
            
            task_id, task_status = await create_veo3_task(
                prompt=state.last_prompt,
                duration=state.video_params.get("duration", 8),
                aspect_ratio=state.video_params.get("aspect_ratio", "9:16"),
                with_audio=state.video_params.get("with_audio", True),
                user_id=user_id
            )
            
            if task_status == "success":
                # Задача создана успешно
                await status_msg.edit_text(
                    f"✨ <b>Ваше видео создается!</b>\n\n"
                    f"{deduction_info}"
                    f"🎬 <b>Описание:</b> {state.last_prompt}\n\n"
                    f"🆔 <b>ID задачи:</b> <code>{task_id}</code>\n\n"
                    f"⏳ <b>Ожидайте уведомление когда видео будет готово (1-2 минуты)</b>\n\n"
                    f"📼 <b>Видео будет отправлено в этот чат автоматически</b>",
                    reply_markup=build_main_menu()
                )
                clear_user_state(user_id)
                return
            else:
                # Ошибка создания задачи
                result = {"error": f"Failed to create VEO 3 task: {task_status}"}
        
        # Обработка ошибок (если дошли сюда)
        if "error" in result:
            await status_msg.edit_text(
                t("video.error", error=result["error"]),
                reply_markup=build_main_menu()
            )
            clear_user_state(user_id)
            return
        
    except Exception as e:
        log.error(f"Ошибка генерации видео: {e}", exc_info=True)
        await status_msg.edit_text(
            t("video.error", error=str(e)),
            reply_markup=build_main_menu()
        )
        clear_user_state(user_id)

async def handle_video_regenerate(callback: CallbackQuery):
    """Повторная генерация видео с теми же параметрами"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    
    if not state.last_prompt:
        await callback.message.edit_text(
            t("error.generation"),
            reply_markup=build_main_menu()
        )
        return
    
    await callback.message.delete()
    await generate_video(callback.message, state)

async def handle_video_to_helper(callback: CallbackQuery):
    """Перейти к режиму помощника"""
    user_id = callback.from_user.id
    state = get_user_state(user_id)
    state.video_mode = "helper"
    state.waiting_for = "prompt_input"
    
    await callback.message.edit_text(
        t("helper.input"),
        reply_markup=build_main_menu()
    )


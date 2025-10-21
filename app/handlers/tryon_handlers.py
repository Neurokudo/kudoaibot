# app/handlers/tryon_handlers.py
"""Обработчики для виртуальной примерочной"""

import logging
import asyncio
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram import F

from app.services import billing
from app.ui.keyboards import btn
from .states import get_user_state, set_user_state, clear_user_state
from .commands import get_user_language

log = logging.getLogger("kudoaibot")

# === ОБРАБОТЧИКИ ПРИМЕРОЧНОЙ ===

async def callback_tryon_start(callback: CallbackQuery):
    """Начать примерку - запрашиваем фото человека"""
    await callback.answer()
    user_id = callback.from_user.id
    user_language = await get_user_language(user_id)
    
    # Инициализируем состояние
    state = get_user_state(user_id)
    state.tryon_data = {
        "person": None,
        "garment": None,
        "dressed": None,
        "stage": "await_person"
    }
    set_user_state(user_id, state)
    
    start_text = "📸 <b>Шаг 1 из 2</b>\n\n"
    start_text += "Отправьте фото человека для примерки.\n\n"
    start_text += "⚠️ Для лучшего результата:\n"
    start_text += "• Портретное фото в полный рост\n"
    start_text += "• Хорошее освещение\n"
    start_text += "• Четкое изображение"
    
    keyboard = [
        [btn("❌ Отменить", "menu_tryon")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        start_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

async def callback_tryon_confirm(callback: CallbackQuery):
    """Подтверждение примерки и запуск генерации"""
    await callback.answer()
    user_id = callback.from_user.id
    
    state = get_user_state(user_id)
    tryon_data = state.tryon_data
    
    if not tryon_data.get("person") or not tryon_data.get("garment"):
        await callback.message.edit_text(
            "❌ Нужно два изображения: человек и одежда.\n\nНачните заново.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🔄 Начать заново", "menu_tryon")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    # Проверяем доступ
    access = await billing.check_access(user_id, "tryon_basic")
    if not access['access']:
        await callback.message.edit_text(
            f"❌ Недостаточно монеток!\n\n"
            f"💰 Нужно: {access.get('cost', 6)} монет\n"
            f"💳 У вас: {access.get('balance', 0)} монет\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💳 Пополнить", "show_topup")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    # Списываем монетки
    deduct_result = await billing.deduct_coins_for_feature(user_id, "tryon_basic")
    
    if not deduct_result['success']:
        await callback.message.edit_text(
            deduct_result['message'],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return
    
    # Информация о списании
    deduction_info = (
        f"💰 <b>Списано:</b> {deduct_result['coins_spent']} монет\n"
        f"💳 <b>Остаток:</b> {deduct_result['balance_after']} монет\n\n"
    )
    
    await callback.message.edit_text("⏳ Делаю примерку… Это может занять до 2 минут.")
    
    try:
        # Запускаем примерку
        from app.services.clients.tryon_client import virtual_tryon
        
        log.info(f"TRYON user {user_id}: Starting virtual try-on")
        
        loop = asyncio.get_event_loop()
        result_bytes = await loop.run_in_executor(
            None,
            virtual_tryon,
            tryon_data["person"],
            tryon_data["garment"],
            1
        )
        
        log.info(f"TRYON user {user_id}: Success, result size: {len(result_bytes)}")
        
        # Сохраняем результат
        tryon_data["dressed"] = result_bytes
        tryon_data["stage"] = "after"
        state.tryon_data = tryon_data
        set_user_state(user_id, state)
        
        # Отправляем результат
        from aiogram.types import BufferedInputFile
        photo_file = BufferedInputFile(result_bytes, filename="tryon_result.png")
        
        result_text = f"✅ <b>Готово! Одежда перенесена на человека.</b>\n\n{deduction_info}"
        result_text += "Что делать дальше?"
        
        keyboard = [
            [btn("🔄 Другая одежда", "tryon_reset")],
            [btn("🏠 Главное меню", "home")]
        ]
        
        await callback.message.answer_photo(
            photo=photo_file,
            caption=result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
        # Удаляем сообщение "Делаю примерку..."
        try:
            await callback.message.delete()
        except:
            pass
            
    except Exception as e:
        log.exception(f"TRYON user {user_id}: Failed with error: {e}")
        
        # Возвращаем монетки
        try:
            from app.services.dual_balance import add_permanent_coins
            await add_permanent_coins(user_id, deduct_result['coins_spent'])
            log.info(f"TRYON user {user_id}: Refunded {deduct_result['coins_spent']} coins")
            
            await callback.message.edit_text(
                f"⚠️ Ошибка примерочной: {str(e)}\n\n"
                f"💰 Возвращено: {deduct_result['coins_spent']} монет\n"
                f"💳 Баланс: {deduct_result['balance_after'] + deduct_result['coins_spent']} монет\n\n"
                f"Попробуйте ещё раз или обратитесь в поддержку.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [btn("🔄 Попробовать снова", "menu_tryon")],
                    [btn("🏠 Главное меню", "home")]
                ])
            )
        except Exception as refund_error:
            log.error(f"TRYON user {user_id}: Refund failed: {refund_error}")
            await callback.message.edit_text(
                f"⚠️ Ошибка примерочной: {str(e)}\n\n"
                f"Обратитесь в поддержку для возврата монет.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [btn("🏠 Главное меню", "home")]
                ])
            )

async def callback_tryon_swap(callback: CallbackQuery):
    """Поменять местами человека и одежду"""
    await callback.answer()
    user_id = callback.from_user.id
    
    state = get_user_state(user_id)
    tryon_data = state.tryon_data
    
    if tryon_data.get("person") and tryon_data.get("garment"):
        # Меняем местами
        tryon_data["person"], tryon_data["garment"] = tryon_data["garment"], tryon_data["person"]
        state.tryon_data = tryon_data
        set_user_state(user_id, state)
        
        await callback.answer("🔄 Изображения поменяны местами", show_alert=True)
        
        # Показываем обновленное подтверждение
        confirm_text = "✅ <b>Фото получены!</b>\n\n"
        confirm_text += "📸 Человек: загружен\n"
        confirm_text += "👕 Одежда: загружена\n\n"
        confirm_text += "💸 <b>Стоимость:</b> 6 монет\n\n"
        confirm_text += "Готовы к примерке?"
        
        keyboard = [
            [btn("✨ Примерить", "tryon_confirm")],
            [btn("🔁 Поменять местами", "tryon_swap")],
            [btn("❌ Сбросить", "tryon_reset")],
            [btn("🏠 Главное меню", "home")]
        ]
        
        await callback.message.edit_text(
            confirm_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await callback.answer("❌ Нужно загрузить оба изображения", show_alert=True)

async def callback_tryon_reset(callback: CallbackQuery):
    """Сбросить примерку и начать заново"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Очищаем состояние
    state = get_user_state(user_id)
    state.tryon_data = {
        "person": None,
        "garment": None,
        "dressed": None,
        "stage": "await_person"
    }
    set_user_state(user_id, state)
    
    reset_text = "🔄 <b>Примерка сброшена</b>\n\n"
    reset_text += "Начнем заново?\n\n"
    reset_text += "📸 Отправьте фото человека для примерки."
    
    keyboard = [
        [btn("📸 Начать", "tryon_start")],
        [btn("🏠 Главное меню", "home")]
    ]
    
    await callback.message.edit_text(
        reset_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# === ОБРАБОТЧИК ФОТО ДЛЯ ПРИМЕРОЧНОЙ ===

async def handle_tryon_photo(message: Message):
    """Обработка фото для примерочной"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    if not state.tryon_data:
        # Не в режиме примерочной
        return False
    
    tryon_data = state.tryon_data
    stage = tryon_data.get("stage")
    
    if stage not in ["await_person", "await_garment"]:
        # Не ожидаем фото
        return False
    
    # Получаем фото
    try:
        from app.core.bot import get_bot
        bot, _ = get_bot()
        
        photo = message.photo[-1]  # Берем самое большое фото
        file = await bot.download(photo.file_id)
        photo_bytes = file.read()
        
        if stage == "await_person":
            # Сохраняем фото человека
            tryon_data["person"] = photo_bytes
            tryon_data["stage"] = "await_garment"
            state.tryon_data = tryon_data
            set_user_state(user_id, state)
            
            person_text = "✅ <b>Фото человека получено!</b>\n\n"
            person_text += "👕 <b>Шаг 2 из 2</b>\n\n"
            person_text += "Теперь отправьте фото одежды.\n\n"
            person_text += "⚠️ Для лучшего результата:\n"
            person_text += "• Одежда на белом фоне\n"
            person_text += "• Четкое изображение\n"
            person_text += "• Хорошо видны детали"
            
            keyboard = [
                [btn("❌ Сбросить", "tryon_reset")],
                [btn("🏠 Главное меню", "home")]
            ]
            
            await message.answer(
                person_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            
        elif stage == "await_garment":
            # Сохраняем фото одежды
            tryon_data["garment"] = photo_bytes
            tryon_data["stage"] = "confirm"
            state.tryon_data = tryon_data
            set_user_state(user_id, state)
            
            confirm_text = "✅ <b>Фото получены!</b>\n\n"
            confirm_text += "📸 Человек: загружен\n"
            confirm_text += "👕 Одежда: загружена\n\n"
            confirm_text += "💸 <b>Стоимость:</b> 6 монет\n\n"
            confirm_text += "Готовы к примерке?"
            
            keyboard = [
                [btn("✨ Примерить", "tryon_confirm")],
                [btn("🔁 Поменять местами", "tryon_swap")],
                [btn("❌ Сбросить", "tryon_reset")],
                [btn("🏠 Главное меню", "home")]
            ]
            
            await message.answer(
                confirm_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        
        return True
        
    except Exception as e:
        log.error(f"Error handling tryon photo for user {user_id}: {e}")
        await message.answer(
            "❌ Ошибка загрузки фото. Попробуйте ещё раз.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("🔄 Начать заново", "menu_tryon")],
                [btn("🏠 Главное меню", "home")]
            ])
        )
        return True


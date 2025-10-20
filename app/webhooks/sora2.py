# app/webhooks/sora2.py
"""Webhook для обработки callback от SORA 2"""

import logging
from aiohttp import web

from app.db import users
from app.ui import t
from app.ui.keyboards import build_video_result_menu
from app.config.pricing import get_feature_cost
from app.services.clients.sora_client import extract_user_from_metadata
from app.core.bot import bot

log = logging.getLogger("kudoaibot")

async def sora2_callback(request):
    """Обработчик callback от OpenAI SORA 2"""
    try:
        data = await request.json()
        log.info(f"🎬 SORA 2 callback received: {data}")
        
        # Получаем данные о видео
        video_id = data.get("id")
        status = data.get("status")
        metadata = data.get("metadata", {})
        
        # Извлекаем user_id
        user_id = extract_user_from_metadata(metadata)
        
        if status == "completed" and user_id:
            # Получаем URL видео
            video_data = data.get("output", {})
            video_url = video_data.get("url")
            
            if video_url:
                # Получаем язык пользователя
                user = await users.get_user(user_id)
                user_language = user.get('language', 'ru') if user else 'ru'
                
                # Отправляем видео пользователю
                try:
                    await bot.send_video(
                        user_id,
                        video=video_url,
                        caption=t("video.success", cost=get_feature_cost("video_8s_audio")),
                        reply_markup=build_video_result_menu(user_language),
                        parse_mode="HTML"
                    )
                    log.info(f"✅ SORA 2 video sent to user {user_id}")
                    
                except Exception as video_error:
                    log.error(f"❌ Failed to send SORA 2 video to user {user_id}: {video_error}")
                    
                    # Fallback - отправляем ссылку
                    try:
                        await bot.send_message(
                            user_id,
                            f"✨ <b>Видео готово!</b>\n\n"
                            f"📹 <a href='{video_url}'>Смотреть видео</a>\n\n"
                            f"💰 Списано: {get_feature_cost('video_8s_audio')} монеток",
                            parse_mode="HTML"
                        )
                    except Exception as fallback_error:
                        log.error(f"❌ Fallback also failed: {fallback_error}")
            else:
                log.error(f"❌ No video URL in SORA 2 callback for user {user_id}")
        
        elif status == "failed" and user_id:
            # Обработка ошибки - возвращаем монетки
            error_data = data.get("error", {})
            error_message = error_data.get("message", "Unknown error")
            
            log.info(f"❌ SORA 2 generation failed for user {user_id}: {error_message}")
            
            # Возвращаем монетки на баланс
            try:
                # Возвращаем стоимость видео используя dual_balance
                cost = get_feature_cost("video_8s_audio")
                from app.services.dual_balance import add_permanent_coins
                
                # Возвращаем как постоянные монетки (не сгорают)
                refund_result = await add_permanent_coins(user_id, cost)
                
                if refund_result['success']:
                    # Уведомляем пользователя
                    await bot.send_message(
                        user_id,
                        f"❌ <b>Ошибка генерации видео SORA 2</b>\n\n"
                        f"Причина: {error_message}\n\n"
                        f"💰 Монетки возвращены на баланс (+{cost} постоянных монеток)",
                        parse_mode="HTML"
                    )
                    log.info(f"✅ Refunded {cost} permanent coins to user {user_id}")
                else:
                    log.error(f"❌ Failed to refund coins to user {user_id}")
                    
            except Exception as refund_error:
                log.error(f"❌ Error refunding coins to user {user_id}: {refund_error}")
        
        else:
            log.info(f"ℹ️ SORA 2 callback status: {status} (user_id: {user_id})")
        
        return web.Response(text="OK")
        
    except Exception as e:
        log.error(f"❌ Error in SORA 2 callback: {e}")
        import traceback
        log.error(f"❌ Traceback: {traceback.format_exc()}")
        return web.Response(text="Error", status=500)


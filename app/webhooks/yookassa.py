# app/webhooks/yookassa.py
"""Webhook для обработки платежей YooKassa"""

import logging
from aiohttp import web

from app.services import billing
from app.config.pricing import get_topup_pack
from app.core.bot import bot

log = logging.getLogger("kudoaibot")

async def yookassa_webhook(request):
    """Обработка webhook от YooKassa"""
    try:
        data = await request.json()
        log.info(f"📥 YooKassa webhook: {data}")
        
        event_type = data.get('event')
        payment_obj = data.get('object', {})
        
        if event_type == 'payment.succeeded':
            payment_id = payment_obj.get('id')
            metadata = payment_obj.get('metadata', {})
            
            user_id = int(metadata.get('user_id'))
            payment_type = metadata.get('payment_type')
            plan_or_coins = metadata.get('plan_or_coins')
            
            if payment_type == 'subscription':
                result = await billing.process_subscription_payment(
                    user_id=user_id,
                    tariff_name=plan_or_coins,
                    payment_id=payment_id
                )
                
                if result['success']:
                    try:
                        await bot.send_message(
                            user_id,
                            result['message']
                        )
                    except Exception as e:
                        log.error(f"Ошибка отправки уведомления: {e}")
                
            elif payment_type == 'topup':
                coins = int(plan_or_coins)
                pack = get_topup_pack(coins)
                
                if pack:
                    result = await billing.process_topup_payment(
                        user_id=user_id,
                        coins=pack.coins,
                        price_rub=pack.price_rub,
                        payment_id=payment_id,
                        bonus_coins=pack.bonus_coins
                    )
                    
                    if result['success']:
                        try:
                            await bot.send_message(
                                user_id,
                                result['message']
                            )
                        except Exception as e:
                            log.error(f"Ошибка отправки уведомления: {e}")
        
        return web.Response(text='OK')
        
    except Exception as e:
        log.error(f"❌ Ошибка обработки webhook: {e}")
        return web.Response(status=500)


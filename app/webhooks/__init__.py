# app/webhooks/__init__.py
"""Webhooks для внешних сервисов"""

from .yookassa import yookassa_webhook
from .sora2 import sora2_callback

__all__ = ['yookassa_webhook', 'sora2_callback']


# app/core/__init__.py
"""Ядро бота - инициализация и настройка"""

from .bot import get_bot, setup_bot_and_dispatcher
from .startup import setup_bot, setup_web_app, graceful_shutdown

__all__ = [
    'get_bot',
    'setup_bot_and_dispatcher',
    'setup_bot',
    'setup_web_app',
    'graceful_shutdown'
]


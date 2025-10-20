# app/handlers/__init__.py
"""Обработчики команд и callback-ов"""

# Импортируем все обработчики для автоматической регистрации
from . import commands
from . import callbacks
from . import payments
from . import text
from . import video_handlers

__all__ = ['commands', 'callbacks', 'payments', 'text', 'video_handlers']


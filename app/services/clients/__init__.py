"""
Клиенты для AI сервисов
"""
from .veo_client import generate_video_sync
from .tryon_client import virtual_tryon

__all__ = [
    'generate_video_sync',
    'virtual_tryon'
]

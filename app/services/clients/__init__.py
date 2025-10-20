"""
Клиенты для AI сервисов
"""
from .veo_client import generate_video_sync, generate_video_veo3_async, create_veo3_task
from .sora_client import generate_video_sora2, generate_video_sora2_async, create_sora_task
from .tryon_client import virtual_tryon

__all__ = [
    'generate_video_sync',
    'generate_video_veo3_async',
    'create_veo3_task',
    'generate_video_sora2',
    'generate_video_sora2_async',
    'create_sora_task',
    'virtual_tryon'
]

# app/ui/callbacks.py
"""Система работы с callback_data для Telegram бота"""

from dataclasses import dataclass
from typing import Optional
import logging

log = logging.getLogger(__name__)

# Разделитель для callback_data
DELIM = "|"

@dataclass
class Cb:
    """Структура для callback данных"""
    action: str
    id: Optional[str] = None
    extra: Optional[str] = None
    
    def pack(self) -> str:
        """Упаковать callback данные в строку"""
        parts = [self.action]
        if self.id:
            parts.append(self.id)
        if self.extra:
            parts.append(self.extra)
        
        raw = DELIM.join(parts)
        
        # Ограничение Telegram на 64 байта
        if len(raw.encode('utf-8')) > 64:
            log.warning(f"Callback data too long: {raw}")
            while len(raw.encode('utf-8')) > 64 and len(parts) > 1:
                parts.pop()
                raw = DELIM.join(parts)
        
        return raw
    
    @classmethod
    def unpack(cls, data: str) -> Optional['Cb']:
        """Распаковать callback данные из строки"""
        try:
            if not data or not isinstance(data, str):
                return None
            
            parts = data.split(DELIM)
            if not parts or not parts[0]:
                return None
            
            while len(parts) < 3:
                parts.append(None)
            return cls(parts[0], parts[1], parts[2])
        except Exception as e:
            log.error(f"Failed to parse callback: {e}")
            return None
    
    def __str__(self) -> str:
        return f"Cb(action={self.action}, id={self.id}, extra={self.extra})"

def parse_cb(data: str) -> Optional[Cb]:
    """Парсер callback данных"""
    if not data:
        return None
    
    cb = Cb.unpack(data)
    if cb:
        log.debug(f"Parsed callback: {cb}")
    
    return cb

# Предопределенные действия
class Actions:
    # Навигация
    NAV = "nav"
    HOME = "home"
    BACK = "back"
    
    # Главное меню
    MENU_VIDEO = "menu_video"
    MENU_PHOTO = "menu_photo"
    MENU_TRYON = "menu_tryon"
    MENU_PROFILE = "menu_profile"
    MENU_TARIFFS = "menu_tariffs"
    
    # Раздел ВИДЕО
    VIDEO_SORA2 = "video_sora2"
    VIDEO_VEO3 = "video_veo3"
    VIDEO_VEO3_FAST = "video_veo3_fast"
    VIDEO_SORA2_PRO = "video_sora2_pro"
    VIDEO_GEMINI = "video_gemini"
    
    # Режимы генерации видео (используются и для VEO 3, и для SORA 2)
    MODE_HELPER = "mode_helper"      # Умный помощник
    MODE_MANUAL = "mode_manual"      # Ручной режим
    MODE_MEME = "mode_meme"          # Мемный режим
    
    # Режимы SORA 2 (с префиксом для различия)
    SORA2_HELPER = "sora2_helper"
    SORA2_MANUAL = "sora2_manual"
    SORA2_MEME = "sora2_meme"
    
    # Параметры видео
    ORIENTATION_PORTRAIT = "ori_916"
    ORIENTATION_LANDSCAPE = "ori_169"
    AUDIO_YES = "audio_yes"
    AUDIO_NO = "audio_no"
    
    # Примерочная
    TRYON_START = "tryon_start"
    TRYON_CONFIRM = "tryon_confirm"
    TRYON_RESET = "tryon_reset"
    
    # Платежи
    PAYMENT_PLANS = "show_plans"
    PAYMENT_TOPUP = "show_topup"
    
    # Дополнительно
    VIDEO_REGENERATE = "video_regenerate"
    VIDEO_TO_HELPER = "video_to_helper"


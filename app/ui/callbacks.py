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
    
    # Выбор языка
    SET_LANGUAGE = "set_language"
    
    # Главное меню (плоская структура)
    MENU_CREATE_VIDEO = "menu_create_video"
    MENU_HELPER = "menu_helper"
    MENU_NEUROKUDO = "menu_neurokudo"
    MENU_MEME = "menu_meme"
    MENU_LEGO = "menu_lego"
    MENU_PHOTO = "menu_photo"
    MENU_TRYON = "menu_tryon"
    MENU_TARIFFS = "menu_tariffs"
    MENU_PROFILE = "menu_profile"
    MENU_HELP = "menu_help"
    
    # Режимы создания видео
    VIDEO_VEO3 = "video_veo3"
    VIDEO_SORA2 = "video_sora2"
    
    # Режимы умного помощника
    HELPER_VEO3 = "helper_veo3"
    HELPER_SORA2 = "helper_sora2"
    
    # Режимы Neurokudo
    NEUROKUDO_VEO3 = "neurokudo_veo3"
    NEUROKUDO_SORA2 = "neurokudo_sora2"
    
    # Режимы мемов
    MEME_VEO3 = "meme_veo3"
    MEME_SORA2 = "meme_sora2"
    
    # LEGO режим
    LEGO_SINGLE = "lego_single"
    LEGO_REPORTAGE = "lego_reportage"
    LEGO_REGENERATE = "lego_regenerate"
    LEGO_IMPROVE = "lego_improve"
    LEGO_EMBED_REPLICA = "lego_embed_replica"
    
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
    
    # Новые действия для упрощенного интерфейса
    SUBSCRIPTIONS = "subscriptions"
    PERMANENT_COINS = "permanent_coins"
    COIN_EXPLANATION = "coin_explanation"
    MODELS_COST = "models_cost"
    
    # Дополнительно
    VIDEO_REGENERATE = "video_regenerate"
    VIDEO_TO_HELPER = "video_to_helper"


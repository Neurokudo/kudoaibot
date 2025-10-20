# app/core/features.py
"""Проверка доступности функций на основе API ключей"""

import os
import logging

log = logging.getLogger("features")

# Проверка API ключей
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GCP_KEY_JSON_B64 = os.getenv("GCP_KEY_JSON_B64")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

class FeatureFlags:
    """Флаги доступности функций"""
    
    @staticmethod
    def has_openai() -> bool:
        """Доступен ли OpenAI (GPT + SORA 2)"""
        return bool(OPENAI_API_KEY)
    
    @staticmethod
    def has_gpt_helper() -> bool:
        """Доступен ли умный помощник"""
        return bool(OPENAI_API_KEY)
    
    @staticmethod
    def has_sora2() -> bool:
        """Доступен ли SORA 2"""
        return bool(OPENAI_API_KEY)
    
    @staticmethod
    def has_veo3() -> bool:
        """Доступен ли VEO 3"""
        return bool(GCP_KEY_JSON_B64)
    
    @staticmethod
    def has_payments() -> bool:
        """Доступны ли платежи"""
        return bool(YOOKASSA_SECRET_KEY)
    
    @staticmethod
    def get_available_video_models() -> list:
        """Получить список доступных моделей видео"""
        models = []
        
        if FeatureFlags.has_veo3():
            models.extend(["veo3_fast", "veo3", "veo3_audio"])
        
        if FeatureFlags.has_sora2():
            models.extend(["sora2", "sora2_pro"])
        
        return models
    
    @staticmethod
    def get_available_modes(model: str) -> list:
        """Получить доступные режимы для модели"""
        modes = ["manual"]  # Ручной режим всегда доступен
        
        if FeatureFlags.has_gpt_helper():
            modes.extend(["helper", "meme"])  # Добавляем режимы с GPT
        
        return modes
    
    @staticmethod
    def get_status_message() -> str:
        """Получить сообщение о статусе доступных функций"""
        lines = ["🔧 <b>Статус функций:</b>\n"]
        
        # OpenAI
        if FeatureFlags.has_openai():
            lines.append("✅ OpenAI: доступен")
            lines.append("  ├ 🤖 Умный помощник: ДА")
            lines.append("  ├ 😄 Мемный режим: ДА")
            lines.append("  └ 🌟 SORA 2: ДА")
        else:
            lines.append("⚠️ OpenAI: НЕ настроен")
            lines.append("  ├ 🤖 Умный помощник: НЕТ")
            lines.append("  ├ 😄 Мемный режим: НЕТ")
            lines.append("  └ 🌟 SORA 2: НЕТ")
        
        # Google Cloud
        if FeatureFlags.has_veo3():
            lines.append("\n✅ Google Cloud: доступен")
            lines.append("  └ 🎥 VEO 3: ДА")
        else:
            lines.append("\n⚠️ Google Cloud: НЕ настроен")
            lines.append("  └ 🎥 VEO 3: НЕТ")
        
        # Платежи
        if FeatureFlags.has_payments():
            lines.append("\n✅ Платежи: доступны")
        else:
            lines.append("\n⚠️ Платежи: НЕ настроены")
        
        # Что работает всегда
        lines.append("\n✅ Доступно всегда:")
        lines.append("  ├ ✋ Ручной режим")
        lines.append("  ├ 👗 Примерочная")
        lines.append("  └ 📸 Фото")
        
        return "\n".join(lines)

# Логирование при импорте
def log_feature_status():
    """Вывести статус функций в лог"""
    log.info("=" * 50)
    log.info("🔧 Проверка доступности функций:")
    log.info(f"  OpenAI (GPT + SORA 2): {'✅' if FeatureFlags.has_openai() else '❌'}")
    log.info(f"  Google Cloud (VEO 3): {'✅' if FeatureFlags.has_veo3() else '❌'}")
    log.info(f"  Платежи (YooKassa): {'✅' if FeatureFlags.has_payments() else '❌'}")
    log.info("=" * 50)

# Вызываем при импорте
log_feature_status()


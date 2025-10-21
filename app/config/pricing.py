"""
Система ценообразования KudoAiBot (финальная версия согласно брифу)
Динамический расчёт стоимости на основе длительности и модели
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

# ===== КОНСТАНТЫ ДЛЯ РАСЧЁТА =====

# Себестоимость в рублях за секунду/операцию
COSTS_RUB = {
    "VEO3_FAST": 9,         # ₽/сек
    "VEO3": 18,             # ₽/сек
    "VEO3_AUDIO": 36,       # ₽/сек
    "SORA2_PRO": 30,        # ₽/сек (27-45 среднее)
    "GEMINI": 13.5,         # ₽/операция
    "IMAGEN_TRYON": 15      # ₽/операция
}

# Стоимость монетки в рублях
COIN_RATE = 3  # 1 монета = 3 рубля

# Целевая маржа (коэффициент)
TARGET_MARGIN = {
    "VEO3_FAST": 3.0,       # 3× маржа
    "VEO3": 2.8,            # 2.8× маржа
    "VEO3_AUDIO": 2.7,      # 2.7× маржа
    "SORA2_PRO": 4.0,       # 4× маржа (премиум)
    "GEMINI": 3.0,          # 3× маржа
    "IMAGEN_TRYON": 3.5     # 3.5× маржа
}

# ===== РАСЧЁТ СТОИМОСТИ В МОНЕТАХ =====

def calculate_coins_per_second(model: str) -> int:
    """
    Рассчитать стоимость в монетах за секунду
    
    Формула: (Себестоимость ₽/сек × Маржа) / Стоимость монетки
    """
    cost_rub = COSTS_RUB.get(model, 0)
    margin = TARGET_MARGIN.get(model, 3.0)
    
    price_rub = cost_rub * margin
    coins = price_rub / COIN_RATE
    
    return int(round(coins))

# Монет за секунду для каждой модели
COINS_PER_SECOND = {
    "VEO3_FAST": calculate_coins_per_second("VEO3_FAST"),    # 3 мон/сек (9×3/3)
    "VEO3": calculate_coins_per_second("VEO3"),              # 5 мон/сек (18×2.8/3)
    "VEO3_AUDIO": calculate_coins_per_second("VEO3_AUDIO"),  # 8 мон/сек (36×2.7/3)
    "SORA2_PRO": calculate_coins_per_second("SORA2_PRO"),    # 12 мон/сек (30×4/3)
}

# Монет за операцию для сервисов
COINS_PER_OPERATION = {
    "GEMINI": int(round(COSTS_RUB["GEMINI"] * TARGET_MARGIN["GEMINI"] / COIN_RATE)),        # 4 мон
    "IMAGEN_TRYON": int(round(COSTS_RUB["IMAGEN_TRYON"] * TARGET_MARGIN["IMAGEN_TRYON"] / COIN_RATE))  # 6 мон
}

@dataclass
class Tariff:
    """Тариф подписки"""
    name: str
    title: str
    price_rub: int
    coins: int              # Подписочные монетки (сгорают через 30 дней)
    duration_days: int
    icon: str
    description: str
    bonus_percent: int = 0

@dataclass
class TopupPack:
    """Пакет пополнения (монетки НЕ сгорают)"""
    coins: int
    price_rub: int
    bonus_coins: int = 0
    bonus_percent: int = 0
    margin_percent: int = 0  # Реальная маржа

# ===== ТАРИФЫ (подписочные монетки, сгорают через 30 дней) =====
TARIFFS: Dict[str, Tariff] = {
    "trial": Tariff(
        name="trial",
        title="Пробный",
        price_rub=390,
        coins=60,
        duration_days=30,
        icon="🌱",
        description="2-3 видео",
        bonus_percent=0
    ),
    "basic": Tariff(
        name="basic",
        title="Базовый",
        price_rub=990,
        coins=180,
        duration_days=30,
        icon="✨",
        description="5-6 видео",
        bonus_percent=20
    ),
    "standard": Tariff(
        name="standard",
        title="Стандарт",
        price_rub=1990,
        coins=400,
        duration_days=30,
        icon="⭐",
        description="12-15 видео",
        bonus_percent=30
    ),
    "premium": Tariff(
        name="premium",
        title="Премиум",
        price_rub=4990,
        coins=1100,
        duration_days=30,
        icon="💎",
        description="30-40 видео",
        bonus_percent=40
    ),
    "pro": Tariff(
        name="pro",
        title="PRO",
        price_rub=7490,
        coins=1600,
        duration_days=30,
        icon="🔥",
        description="20-25 HQ видео",
        bonus_percent=50
    )
}

# ===== ПАКЕТЫ ПОПОЛНЕНИЯ (постоянные монетки, НЕ сгорают) =====
# Согласно follow-up брифу: бонусы 0%, 8%, 12%, 15%
TOPUP_PACKS: List[TopupPack] = [
    TopupPack(coins=50, price_rub=990, bonus_coins=0, bonus_percent=0, margin_percent=40),
    TopupPack(coins=120, price_rub=1990, bonus_coins=10, bonus_percent=8, margin_percent=45),   # 120 + 10 = 130
    TopupPack(coins=250, price_rub=3990, bonus_coins=30, bonus_percent=12, margin_percent=50),  # 250 + 30 = 280
    TopupPack(coins=500, price_rub=7490, bonus_coins=75, bonus_percent=15, margin_percent=55),  # 500 + 75 = 575
]

# ===== СТОИМОСТЬ ФУНКЦИЙ (динамический расчёт) =====

def calculate_video_cost(model: str, duration_seconds: int) -> int:
    """
    Рассчитать стоимость видео в монетах
    
    Формула: COINS_PER_SECOND[model] × duration_seconds
    
    Args:
        model: Название модели (VEO3_FAST, VEO3, VEO3_AUDIO, SORA2_PRO)
        duration_seconds: Длительность в секундах
    
    Returns:
        Стоимость в монетах
    """
    coins_per_sec = COINS_PER_SECOND.get(model, 5)
    return coins_per_sec * duration_seconds

# Предустановленные стоимости для популярных комбинаций
FEATURE_COSTS: Dict[str, int] = {
    # === VEO 3 FAST (3 мон/сек) ===
    "veo3_fast_6s": calculate_video_cost("VEO3_FAST", 6),   # 18 монет
    "veo3_fast_8s": calculate_video_cost("VEO3_FAST", 8),   # 24 монеты
    
    # === VEO 3 (5 мон/сек) ===
    "veo3_6s": calculate_video_cost("VEO3", 6),             # 30 монет
    "veo3_8s": calculate_video_cost("VEO3", 8),             # 40 монет
    
    # === VEO 3 AUDIO (8 мон/сек) ===
    "veo3_audio_6s": calculate_video_cost("VEO3_AUDIO", 6), # 48 монет
    "veo3_audio_8s": calculate_video_cost("VEO3_AUDIO", 8), # 64 монеты
    
    # === SORA 2 PRO (12 мон/сек) ===
    "sora2_pro_5s": calculate_video_cost("SORA2_PRO", 5),   # 60 монет
    "sora2_pro_10s": calculate_video_cost("SORA2_PRO", 10), # 120 монет
    "sora2_pro_20s": calculate_video_cost("SORA2_PRO", 20), # 240 монет
    
    # === ФОТО (Gemini) - 4 мон/операция ===
    "photo_enhance": COINS_PER_OPERATION["GEMINI"],         # 4 монеты
    "photo_remove_bg": COINS_PER_OPERATION["GEMINI"],       # 4 монеты
    "photo_retouch": COINS_PER_OPERATION["GEMINI"],         # 4 монеты
    "photo_style": COINS_PER_OPERATION["GEMINI"],           # 4 монеты
    
    # === ПРИМЕРОЧНАЯ (Imagen Try-On) ===
    "tryon_basic": 6,          # 1 образ
    "tryon_fashion": 10,       # Модный стиль
    "tryon_pro": 15,           # 3 образа (Imagen Pro)
    
    # Обратная совместимость
    "video_6s_mute": 30,       # Veo 3
    "video_8s_mute": 40,       # Veo 3
    "video_8s_audio": 64,      # Veo 3 Audio
    "virtual_tryon": 6,        # Try-On базовый
}

# ===== ОПИСАНИЯ С ДЕТАЛИЗАЦИЕЙ =====
FEATURE_DESCRIPTIONS: Dict[str, str] = {
    # Видео
    "veo3_fast_6s": "⚡ Veo 3 Fast (6 сек) — 3 мон/сек",
    "veo3_fast_8s": "⚡ Veo 3 Fast (8 сек) — 3 мон/сек",
    "veo3_6s": "🎥 Veo 3 (6 сек) — 5 мон/сек",
    "veo3_8s": "🎥 Veo 3 (8 сек) — 5 мон/сек",
    "veo3_audio_6s": "🎬 Veo 3 Audio (6 сек) — 8 мон/сек",
    "veo3_audio_8s": "🎬 Veo 3 Audio (8 сек) — 8 мон/сек",
    "sora2_pro_5s": "🔥 Sora 2 Pro (5 сек) — 12 мон/сек",
    "sora2_pro_10s": "🔥 Sora 2 Pro (10 сек) — 12 мон/сек",
    "sora2_pro_20s": "🔥 Sora 2 Pro (20 сек) — 12 мон/сек",
    
    # Фото
    "photo_enhance": "🪄 Gemini Enhance — 4 мон/операция",
    "photo_remove_bg": "🪄 Gemini Remove BG — 4 мон/операция",
    "photo_retouch": "🪄 Gemini Retouch — 4 мон/операция",
    "photo_style": "🪄 Gemini Style — 4 мон/операция",
    
    # Примерочная
    "tryon_basic": "👗 Imagen Try-On — 6 мон (1 образ)",
    "tryon_fashion": "👗 Imagen Fashion — 10 мон",
    "tryon_pro": "👗 Imagen Pro — 15 мон (3 образа)",
}

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_tariff_info(tariff_name: str) -> Optional[Tariff]:
    """Получить информацию о тарифе"""
    return TARIFFS.get(tariff_name)

def get_feature_cost(feature: str) -> int:
    """Получить стоимость функции в монетках"""
    return FEATURE_COSTS.get(feature, 1)

def get_dynamic_video_cost(model: str, duration: int) -> int:
    """
    Рассчитать стоимость видео динамически
    
    Args:
        model: VEO3_FAST, VEO3, VEO3_AUDIO, SORA2_PRO
        duration: Длительность в секундах
    
    Returns:
        Стоимость в монетах
    """
    return calculate_video_cost(model, duration)

def get_feature_description(feature: str) -> str:
    """Получить описание функции"""
    return FEATURE_DESCRIPTIONS.get(feature, feature)

def get_topup_pack(coins: int) -> Optional[TopupPack]:
    """Получить пакет пополнения по количеству монеток"""
    for pack in TOPUP_PACKS:
        if pack.coins == coins:
            return pack
    return None

def format_price(price_rub: int) -> str:
    """Форматировать цену в рублях"""
    return f"{price_rub:,} ₽".replace(",", " ")

def calculate_margin(feature: str) -> float:
    """
    Рассчитать маржу для функции в процентах
    
    Формула: ((Выручка - Себестоимость) / Себестоимость) × 100
    """
    coins = FEATURE_COSTS.get(feature, 0)
    revenue_rub = coins * COIN_RATE
    
    # Определяем модель для получения себестоимости
    if "veo3_fast" in feature:
        model_key = "VEO3_FAST"
        duration = 6 if "6s" in feature else 8
        cogs_rub = COSTS_RUB[model_key] * duration
    elif "veo3_audio" in feature:
        model_key = "VEO3_AUDIO"
        duration = 6 if "6s" in feature else 8
        cogs_rub = COSTS_RUB[model_key] * duration
    elif "veo3" in feature:
        model_key = "VEO3"
        duration = 6 if "6s" in feature else 8
        cogs_rub = COSTS_RUB[model_key] * duration
    elif "sora2" in feature:
        model_key = "SORA2_PRO"
        if "5s" in feature:
            duration = 5
        elif "10s" in feature:
            duration = 10
        else:
            duration = 20
        cogs_rub = COSTS_RUB[model_key] * duration
    elif "photo" in feature:
        cogs_rub = COSTS_RUB["GEMINI"]
    elif "tryon" in feature:
        cogs_rub = COSTS_RUB["IMAGEN_TRYON"]
    else:
        return 0
    
    if cogs_rub == 0:
        return 0
    
    margin = ((revenue_rub - cogs_rub) / cogs_rub) * 100
    return round(margin, 1)

def format_tariffs_text() -> str:
    """Форматированный текст с тарифами"""
    from app.utils.formatting import format_coins
    
    lines = ["💎 <b>Подписки на 30 дней</b>"]
    lines.append("🟢 Подписочные монетки сгорают через 30 дней\n")
    
    for key, tariff in TARIFFS.items():
        lines.append(f"{tariff.icon} <b>{tariff.title}</b> — {format_price(tariff.price_rub)}")
        lines.append(f"├ {format_coins(tariff.coins, short=True)}")
        
        if tariff.bonus_percent > 0:
            lines.append(f"├ 🎁 Бонус +{tariff.bonus_percent}%")
        
        lines.append(f"└ {tariff.description}\n")
    
    return "\n".join(lines)

def format_topup_packs_text() -> str:
    """Форматированный текст с пакетами пополнения"""
    from app.utils.formatting import format_coins
    
    lines = ["💰 <b>Пакеты пополнения</b>"]
    lines.append("🟣 Постоянные монетки НЕ сгорают никогда!\n")
    
    for pack in TOPUP_PACKS:
        total_coins = pack.coins + pack.bonus_coins
        if pack.bonus_coins > 0:
            lines.append(
                f"• <b>{format_coins(total_coins, short=True)}</b> "
                f"({pack.coins} + {pack.bonus_coins} бонус 🎁) — "
                f"{format_price(pack.price_rub)} | Бонус: +{pack.bonus_percent}% | Маржа: ~{pack.margin_percent}%"
            )
        else:
            lines.append(
                f"• <b>{format_coins(pack.coins, short=True)}</b> — "
                f"{format_price(pack.price_rub)} | Маржа: ~{pack.margin_percent}%"
            )
    
    lines.append("\n💡 Работают без подписки и остаются навсегда!")
    
    return "\n".join(lines)

def format_feature_costs_text() -> str:
    """Форматированный текст со стоимостью функций"""
    lines = ["💡 <b>Стоимость генераций:</b>\n"]
    
    # Видео
    lines.append("🎬 <b>Видео:</b>")
    lines.append(f"⚡ Veo 3 Fast — <b>3 монетки за секунду</b> (6 сек = {FEATURE_COSTS['veo3_fast_6s']} монеток, 8 сек = {FEATURE_COSTS['veo3_fast_8s']} монеток)")
    lines.append(f"🎥 Veo 3 — <b>5 монеток за секунду</b> (6 сек = {FEATURE_COSTS['veo3_6s']} монеток, 8 сек = {FEATURE_COSTS['veo3_8s']} монеток)")
    lines.append(f"🎬 Veo 3 Audio — <b>8 монеток за секунду</b> (6 сек = {FEATURE_COSTS['veo3_audio_6s']} монеток, 8 сек = {FEATURE_COSTS['veo3_audio_8s']} монеток)")
    lines.append(f"🔥 Sora 2 Pro — <b>12 монеток за секунду</b> (5 сек = {FEATURE_COSTS['sora2_pro_5s']} монеток, 10 сек = {FEATURE_COSTS['sora2_pro_10s']} монеток, 20 сек = {FEATURE_COSTS['sora2_pro_20s']} монеток)\n")
    
    # Фото
    lines.append("📸 <b>Фото (Gemini):</b>")
    lines.append(f"🪄 Enhance / Remove BG / Retouch / Style — <b>4 монетки за операцию</b>\n")
    
    # Примерочная
    lines.append("👗 <b>Виртуальная примерочная:</b>")
    lines.append(f"• Imagen Try-On (1 образ) — <b>6 монеток</b>")
    lines.append(f"• Imagen Fashion — <b>10 монеток</b>")
    lines.append(f"• Imagen Pro (3 образа) — <b>15 монеток</b>\n")
    
    return "\n".join(lines)

def get_full_pricing_text() -> str:
    """Полный текст с ценами"""
    return "\n".join([
        format_tariffs_text(),
        "",
        format_topup_packs_text(),
        "",
        format_feature_costs_text(),
    ])

# ===== РАСЧЁТ СЕБЕСТОИМОСТИ И МАРЖИ =====

def get_cost_breakdown(feature: str) -> Dict:
    """
    Получить детальный breakdown себестоимости и маржи
    
    Returns:
        {
            'coins': int,
            'revenue_rub': float,
            'cogs_rub': float,
            'margin_rub': float,
            'margin_percent': float
        }
    """
    coins = FEATURE_COSTS.get(feature, 0)
    revenue_rub = coins * COIN_RATE
    
    # Определяем себестоимость
    if "veo3_fast" in feature:
        duration = 6 if "6s" in feature else 8
        cogs_rub = COSTS_RUB["VEO3_FAST"] * duration
    elif "veo3_audio" in feature:
        duration = 6 if "6s" in feature else 8
        cogs_rub = COSTS_RUB["VEO3_AUDIO"] * duration
    elif "veo3" in feature:
        duration = 6 if "6s" in feature else 8
        cogs_rub = COSTS_RUB["VEO3"] * duration
    elif "sora2" in feature:
        if "5s" in feature:
            duration = 5
        elif "10s" in feature:
            duration = 10
        else:
            duration = 20
        cogs_rub = COSTS_RUB["SORA2_PRO"] * duration
    elif "photo" in feature:
        cogs_rub = COSTS_RUB["GEMINI"]
    elif "tryon" in feature:
        if "pro" in feature:
            cogs_rub = COSTS_RUB["IMAGEN_TRYON"] * 3
        else:
            cogs_rub = COSTS_RUB["IMAGEN_TRYON"]
    else:
        cogs_rub = 0
    
    margin_rub = revenue_rub - cogs_rub
    margin_percent = (margin_rub / cogs_rub * 100) if cogs_rub > 0 else 0
    
    return {
        'coins': coins,
        'revenue_rub': revenue_rub,
        'cogs_rub': cogs_rub,
        'margin_rub': margin_rub,
        'margin_percent': round(margin_percent, 1)
    }

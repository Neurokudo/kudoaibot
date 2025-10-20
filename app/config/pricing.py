"""
Система ценообразования KudoAiBot (обновлённая версия)
Две системы монеток: подписочные (сгорают) и купленные (вечные)
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Tariff:
    """Тариф подписки (монетки сгорают через 30 дней)"""
    name: str
    title: str
    price_rub: int
    coins: int              # Подписочные монетки
    duration_days: int
    icon: str
    description: str
    bonus_percent: int = 0  # Процент бонуса

@dataclass
class TopupPack:
    """Пакет пополнения (монетки НЕ сгорают)"""
    coins: int
    price_rub: int
    bonus_coins: int = 0    # Бонусные монетки при покупке
    bonus_percent: int = 0  # Процент бонуса для отображения

@dataclass
class FeatureCost:
    """Стоимость функции"""
    feature: str
    coins: int
    description: str
    category: str
    cogs_usd: float  # Себестоимость в USD

# ===== ТАРИФЫ НА ПОДПИСКУ (монетки сгорают через 30 дней) =====
TARIFFS: Dict[str, Tariff] = {
    "trial": Tariff(
        name="trial",
        title="Пробный",
        price_rub=390,
        coins=60,
        duration_days=30,
        icon="🌱",
        description="Попробовать возможности бота",
        bonus_percent=0
    ),
    "basic": Tariff(
        name="basic",
        title="Базовый",
        price_rub=990,
        coins=180,
        duration_days=30,
        icon="✨",
        description="Для регулярного использования",
        bonus_percent=20
    ),
    "standard": Tariff(
        name="standard",
        title="Стандарт",
        price_rub=1990,
        coins=400,
        duration_days=30,
        icon="⭐",
        description="Оптимальный выбор для активных пользователей",
        bonus_percent=30
    ),
    "premium": Tariff(
        name="premium",
        title="Премиум",
        price_rub=4990,
        coins=1100,
        duration_days=30,
        icon="💎",
        description="Максимум возможностей",
        bonus_percent=40
    ),
    "pro_sora": Tariff(
        name="pro_sora",
        title="PRO Sora 2",
        price_rub=7490,
        coins=1600,
        duration_days=30,
        icon="🔥",
        description="Для профессионалов - HQ видео Sora 2 Pro",
        bonus_percent=50
    )
}

# ===== СТОИМОСТЬ ФУНКЦИЙ В МОНЕТКАХ =====
# Расчёт: себестоимость × маржа (2.5-4.5x)
FEATURE_COSTS: Dict[str, int] = {
    # === ВИДЕО ===
    # Veo 3 Fast (9 ₽/сек → 3 мон/сек)
    "veo3_fast_6s": 18,        # 6 сек × 3 = 18 монет
    "veo3_fast_8s": 24,        # 8 сек × 3 = 24 монеты
    
    # Veo 3 (18 ₽/сек → 5 мон/сек)
    "veo3_6s": 30,             # 6 сек × 5 = 30 монет
    "veo3_8s": 40,             # 8 сек × 5 = 40 монет
    
    # Veo 3 Audio (36 ₽/сек → 8 мон/сек)
    "veo3_audio_6s": 48,       # 6 сек × 8 = 48 монет
    "veo3_audio_8s": 64,       # 8 сек × 8 = 64 монеты
    
    # Sora 2 Pro (27-45 ₽/сек → 12 мон/сек)
    "sora2_pro_5s": 60,        # 5 сек × 12 = 60 монет
    "sora2_pro_10s": 120,      # 10 сек × 12 = 120 монет
    "sora2_pro_20s": 240,      # 20 сек × 12 = 240 монет
    
    # === ФОТО ===
    # Gemini (13.5 ₽/операция → 4 монетки)
    "photo_enhance": 4,        # Улучшение фото
    "photo_remove_bg": 4,      # Удаление фона
    "photo_retouch": 4,        # Ретушь
    "photo_style": 4,          # Смена стиля
    
    # === ПРИМЕРОЧНАЯ ===
    # Imagen Try-On
    "tryon_basic": 6,          # 1 образ (12 ₽ → 6 монет)
    "tryon_pro": 15,           # 3 образа (30 ₽ → 15 монет)
    "tryon_fashion": 10,       # Модный стиль
    
    # Обратная совместимость (старые названия)
    "video_6s_mute": 30,       # Veo 3
    "video_8s_mute": 40,       # Veo 3
    "video_8s_audio": 64,      # Veo 3 Audio
    "virtual_tryon": 6,        # Try-On базовый
}

# ===== ОПИСАНИЯ ФУНКЦИЙ =====
FEATURE_DESCRIPTIONS: Dict[str, str] = {
    # Видео
    "veo3_fast_6s": "🎬 Veo 3 Fast (6 сек)",
    "veo3_fast_8s": "🎬 Veo 3 Fast (8 сек)",
    "veo3_6s": "🎬 Veo 3 (6 сек)",
    "veo3_8s": "🎬 Veo 3 (8 сек)",
    "veo3_audio_6s": "🎬 Veo 3 Audio (6 сек, со звуком)",
    "veo3_audio_8s": "🎬 Veo 3 Audio (8 сек, со звуком)",
    "sora2_pro_5s": "🌟 Sora 2 Pro (5 сек)",
    "sora2_pro_10s": "🌟 Sora 2 Pro (10 сек)",
    "sora2_pro_20s": "🌟 Sora 2 Pro (20 сек)",
    
    # Фото
    "photo_enhance": "📸 Улучшение фото",
    "photo_remove_bg": "📸 Удаление фона",
    "photo_retouch": "📸 Ретушь",
    "photo_style": "📸 Смена стиля",
    
    # Примерочная
    "tryon_basic": "👗 Примерочная (1 образ)",
    "tryon_pro": "👗 Примерочная (3 образа)",
    "tryon_fashion": "👗 Модный стиль",
}

# ===== СЕБЕСТОИМОСТЬ В USD =====
COGS_USD: Dict[str, float] = {
    # Видео (из брифа)
    "veo3_fast_6s": 0.60,      # 9 ₽/сек × 6 сек / 90
    "veo3_fast_8s": 0.80,      # 9 ₽/сек × 8 сек / 90
    "veo3_6s": 1.20,           # 18 ₽/сек × 6 сек / 90
    "veo3_8s": 1.60,           # 18 ₽/сек × 8 сек / 90
    "veo3_audio_6s": 2.40,     # 36 ₽/сек × 6 сек / 90
    "veo3_audio_8s": 3.20,     # 36 ₽/сек × 8 сек / 90
    "sora2_pro_5s": 1.50,      # 27 ₽/сек × 5 сек / 90
    "sora2_pro_10s": 3.00,     # 27 ₽/сек × 10 сек / 90
    "sora2_pro_20s": 6.00,     # 27 ₽/сек × 20 сек / 90
    
    # Фото
    "photo_enhance": 0.15,     # 13.5 ₽ / 90
    "photo_remove_bg": 0.15,
    "photo_retouch": 0.15,
    "photo_style": 0.15,
    
    # Примерочная
    "tryon_basic": 0.13,       # 12 ₽ / 90
    "tryon_pro": 0.33,         # 30 ₽ / 90
    "tryon_fashion": 0.22,
}

# ===== ПАКЕТЫ ПОПОЛНЕНИЯ (монетки НЕ сгорают) =====
TOPUP_PACKS: List[TopupPack] = [
    TopupPack(coins=50, price_rub=990, bonus_coins=0, bonus_percent=0),
    TopupPack(coins=120, price_rub=1990, bonus_coins=10, bonus_percent=8),
    TopupPack(coins=250, price_rub=3990, bonus_coins=30, bonus_percent=12),
    TopupPack(coins=500, price_rub=7490, bonus_coins=75, bonus_percent=15),
]

# ===== КАТЕГОРИИ ФУНКЦИЙ =====
FEATURE_CATEGORIES: Dict[str, List[str]] = {
    "video_fast": ["veo3_fast_6s", "veo3_fast_8s"],
    "video_standard": ["veo3_6s", "veo3_8s"],
    "video_audio": ["veo3_audio_6s", "veo3_audio_8s"],
    "video_sora": ["sora2_pro_5s", "sora2_pro_10s", "sora2_pro_20s"],
    "photo": ["photo_enhance", "photo_remove_bg", "photo_retouch", "photo_style"],
    "tryon": ["tryon_basic", "tryon_pro", "tryon_fashion"],
}

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_tariff_info(tariff_name: str) -> Optional[Tariff]:
    """Получить информацию о тарифе"""
    return TARIFFS.get(tariff_name)

def get_feature_cost(feature: str) -> int:
    """Получить стоимость функции в монетках"""
    return FEATURE_COSTS.get(feature, 1)

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

def calculate_video_count(coins: int, feature: str = "veo3_8s") -> int:
    """Рассчитать количество видео для тарифа"""
    cost = get_feature_cost(feature)
    return coins // cost if cost > 0 else 0

def format_tariffs_text() -> str:
    """Форматированный текст с тарифами"""
    lines = ["💎 <b>Подписки на 30 дней</b>"]
    lines.append("🟢 Монетки сгорают через 30 дней\n")
    
    for key, tariff in TARIFFS.items():
        video_count = calculate_video_count(tariff.coins, "veo3_8s")
        
        lines.append(f"{tariff.icon} <b>{tariff.title}</b> — {format_price(tariff.price_rub)}")
        lines.append(f"├ {tariff.coins} монеток")
        
        if tariff.bonus_percent > 0:
            lines.append(f"├ 🎁 Бонус +{tariff.bonus_percent}%")
        
        lines.append(f"└ Примерно {video_count} видео (8 сек)\n")
    
    return "\n".join(lines)

def format_topup_packs_text() -> str:
    """Форматированный текст с пакетами пополнения"""
    lines = ["💰 <b>Пакеты пополнения</b>"]
    lines.append("🟣 Монетки НЕ сгорают никогда!\n")
    
    for pack in TOPUP_PACKS:
        total_coins = pack.coins + pack.bonus_coins
        if pack.bonus_coins > 0:
            lines.append(
                f"• {total_coins} монет ({pack.coins} + {pack.bonus_coins} бонус 🎁) — "
                f"{format_price(pack.price_rub)}"
            )
        else:
            lines.append(f"• {pack.coins} монет — {format_price(pack.price_rub)}")
    
    lines.append("\n💡 Монетки остаются навсегда и работают без подписки!")
    
    return "\n".join(lines)

def format_feature_costs_text() -> str:
    """Форматированный текст со стоимостью функций"""
    lines = ["💡 <b>Стоимость генераций:</b>\n"]
    
    # Видео
    lines.append("🎬 <b>Видео Veo 3 Fast:</b>")
    lines.append(f"• 6 сек — {FEATURE_COSTS['veo3_fast_6s']} монет (3 мон/сек)")
    lines.append(f"• 8 сек — {FEATURE_COSTS['veo3_fast_8s']} монет\n")
    
    lines.append("🎬 <b>Видео Veo 3:</b>")
    lines.append(f"• 6 сек — {FEATURE_COSTS['veo3_6s']} монет (5 мон/сек)")
    lines.append(f"• 8 сек — {FEATURE_COSTS['veo3_8s']} монет\n")
    
    lines.append("🎬 <b>Видео Veo 3 Audio:</b>")
    lines.append(f"• 6 сек — {FEATURE_COSTS['veo3_audio_6s']} монет (8 мон/сек)")
    lines.append(f"• 8 сек — {FEATURE_COSTS['veo3_audio_8s']} монет\n")
    
    lines.append("🌟 <b>Sora 2 Pro:</b>")
    lines.append(f"• 5 сек — {FEATURE_COSTS['sora2_pro_5s']} монет (12 мон/сек)")
    lines.append(f"• 10 сек — {FEATURE_COSTS['sora2_pro_10s']} монет")
    lines.append(f"• 20 сек — {FEATURE_COSTS['sora2_pro_20s']} монет\n")
    
    # Фото
    lines.append("📸 <b>Фото (Gemini):</b>")
    lines.append(f"• Улучшение — {FEATURE_COSTS['photo_enhance']} монеты")
    lines.append(f"• Удаление фона — {FEATURE_COSTS['photo_remove_bg']} монеты")
    lines.append(f"• Ретушь — {FEATURE_COSTS['photo_retouch']} монеты\n")
    
    # Примерочная
    lines.append("👗 <b>Виртуальная примерочная:</b>")
    lines.append(f"• 1 образ — {FEATURE_COSTS['tryon_basic']} монет")
    lines.append(f"• 3 образа — {FEATURE_COSTS['tryon_pro']} монет")
    lines.append(f"• Модный стиль — {FEATURE_COSTS['tryon_fashion']} монет\n")
    
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

def calculate_margin(feature: str) -> float:
    """Рассчитать маржу для функции"""
    cost_coins = FEATURE_COSTS.get(feature, 0)
    cogs = COGS_USD.get(feature, 0)
    
    if cogs == 0:
        return 0
    
    # Примерная стоимость монетки ~18-20 ₽
    # Для расчёта берём среднюю стоимость из тарифа "Стандарт"
    coin_price_rub = TARIFFS["standard"].price_rub / TARIFFS["standard"].coins  # ~4.97 ₽/монетка
    
    revenue_rub = cost_coins * coin_price_rub
    cogs_rub = cogs * 90  # USD → RUB
    
    margin = ((revenue_rub - cogs_rub) / cogs_rub) * 100 if cogs_rub > 0 else 0
    
    return round(margin, 1)

"""
Система ценообразования KudoAiBot
Все тарифы, стоимости функций и пакеты пополнения
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Tariff:
    """Тариф подписки"""
    name: str
    title: str
    price_rub: int
    coins: int
    duration_days: int
    icon: str
    description: str

@dataclass
class TopupPack:
    """Пакет пополнения монеток"""
    coins: int
    price_rub: int
    bonus_coins: int = 0  # Бонусные монетки при покупке

@dataclass
class FeatureCost:
    """Стоимость функции"""
    feature: str
    coins: int
    description: str
    category: str

# ===== ТАРИФЫ НА ПОДПИСКУ (30 дней) =====
TARIFFS: Dict[str, Tariff] = {
    "lite": Tariff(
        name="lite",
        title="Лайт",
        price_rub=1990,
        coins=250,
        duration_days=30,
        icon="✨",
        description="Базовый тариф для начинающих"
    ),
    "standard": Tariff(
        name="standard",
        title="Стандарт",
        price_rub=2990,
        coins=400,
        duration_days=30,
        icon="⭐",
        description="Оптимальный тариф для регулярного использования"
    ),
    "pro": Tariff(
        name="pro",
        title="Про",
        price_rub=4990,
        coins=750,
        duration_days=30,
        icon="💎",
        description="Максимальный тариф для профессионалов"
    )
}

# ===== СТОИМОСТЬ ФУНКЦИЙ В МОНЕТКАХ =====
FEATURE_COSTS: Dict[str, int] = {
    # Видео Veo 3
    "video_6s_mute": 14,      # 6 сек без звука
    "video_8s_mute": 18,      # 8 сек без звука
    "video_8s_audio": 26,     # 8 сек со звуком
    
    # Фото-инструменты
    "image_basic": 1,         # Базовые операции с фото
    "image_upscale": 2,       # Увеличение качества
    "image_enhance": 3,       # Улучшение фото
    
    # Виртуальная примерочная
    "virtual_tryon": 3,       # Try-On (1 результат)
    "virtual_tryon_batch": 8, # Try-On (3 результата)
    
    # Другие функции
    "json_generation": 26,    # Генерация JSON для видео
}

# ===== ОПИСАНИЯ ФУНКЦИЙ =====
FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "video_6s_mute": "🎬 Видео Veo 3 (6 сек, без звука)",
    "video_8s_mute": "🎬 Видео Veo 3 (8 сек, без звука)",
    "video_8s_audio": "🎬 Видео Veo 3 (8 сек, со звуком)",
    "image_basic": "📸 Базовые операции с фото",
    "image_upscale": "📸 Увеличение качества фото",
    "image_enhance": "📸 Улучшение фото",
    "virtual_tryon": "👗 Виртуальная примерочная (1 образ)",
    "virtual_tryon_batch": "👗 Виртуальная примерочная (3 образа)",
    "json_generation": "🔧 JSON генерация для видео",
}

# ===== ПАКЕТЫ ПОПОЛНЕНИЯ МОНЕТОК =====
TOPUP_PACKS: List[TopupPack] = [
    TopupPack(coins=50, price_rub=990, bonus_coins=0),
    TopupPack(coins=120, price_rub=1990, bonus_coins=10),
    TopupPack(coins=250, price_rub=3990, bonus_coins=30),
    TopupPack(coins=500, price_rub=7490, bonus_coins=75),
]

# ===== КАТЕГОРИИ ФУНКЦИЙ =====
FEATURE_CATEGORIES: Dict[str, List[str]] = {
    "video": ["video_6s_mute", "video_8s_mute", "video_8s_audio"],
    "photo": ["image_basic", "image_upscale", "image_enhance"],
    "tryon": ["virtual_tryon", "virtual_tryon_batch"],
    "other": ["json_generation"],
}

# ===== СЕБЕСТОИМОСТЬ (для аналитики) =====
COGS_USD: Dict[str, float] = {
    "video_6s_mute": 0.70,
    "video_8s_mute": 0.80,
    "video_8s_audio": 1.20,
    "image_basic": 0.02,
    "image_upscale": 0.04,
    "image_enhance": 0.06,
    "virtual_tryon": 0.12,
    "virtual_tryon_batch": 0.30,
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

def calculate_tariff_examples(coins: int) -> Dict[str, int]:
    """Рассчитать примеры использования для тарифа"""
    return {
        "video_6s_mute": coins // FEATURE_COSTS["video_6s_mute"],
        "video_8s_mute": coins // FEATURE_COSTS["video_8s_mute"],
        "video_8s_audio": coins // FEATURE_COSTS["video_8s_audio"],
        "virtual_tryon": coins // FEATURE_COSTS["virtual_tryon"],
        "image_basic": coins // FEATURE_COSTS["image_basic"],
    }

def format_tariffs_text() -> str:
    """Форматированный текст с тарифами"""
    lines = ["💰 <b>Тарифы на 30 дней</b>\n"]
    
    for key, tariff in TARIFFS.items():
        lines.append(f"{tariff.icon} <b>{tariff.title}</b> — {format_price(tariff.price_rub)}")
        lines.append(f"├ {tariff.coins} монеток")
        lines.append(f"└ {tariff.description}\n")
        
        examples = calculate_tariff_examples(tariff.coins)
        lines.append("Что можно сделать:")
        lines.append(f"• до {examples['video_8s_audio']} видео (8 сек, со звуком)")
        lines.append(f"• или до {examples['video_8s_mute']} видео (8 сек, без звука)")
        lines.append(f"• или до {examples['virtual_tryon']} виртуальных примерок")
        lines.append(f"• или до {examples['image_basic']} фото-операций")
        lines.append("")
    
    return "\n".join(lines)

def format_feature_costs_text() -> str:
    """Форматированный текст со стоимостью функций"""
    lines = ["💡 <b>Стоимость функций:</b>\n"]
    
    # Видео
    lines.append("🎬 <b>Видео Veo 3:</b>")
    lines.append(f"• 6 сек без звука — {FEATURE_COSTS['video_6s_mute']} монеток")
    lines.append(f"• 8 сек без звука — {FEATURE_COSTS['video_8s_mute']} монеток")
    lines.append(f"• 8 сек со звуком — {FEATURE_COSTS['video_8s_audio']} монеток\n")
    
    # Фото
    lines.append("📸 <b>Фото-инструменты:</b>")
    lines.append(f"• Базовые операции — {FEATURE_COSTS['image_basic']} монетка")
    lines.append(f"• Увеличение качества — {FEATURE_COSTS['image_upscale']} монетки")
    lines.append(f"• Улучшение фото — {FEATURE_COSTS['image_enhance']} монетки\n")
    
    # Try-On
    lines.append("👗 <b>Виртуальная примерочная:</b>")
    lines.append(f"• 1 образ — {FEATURE_COSTS['virtual_tryon']} монетки")
    lines.append(f"• 3 образа — {FEATURE_COSTS['virtual_tryon_batch']} монеток\n")
    
    return "\n".join(lines)

def format_topup_packs_text() -> str:
    """Форматированный текст с пакетами пополнения"""
    lines = ["➕ <b>Пакеты пополнения:</b>\n"]
    
    for pack in TOPUP_PACKS:
        total_coins = pack.coins + pack.bonus_coins
        if pack.bonus_coins > 0:
            lines.append(
                f"• {total_coins} монеток ({pack.coins} + {pack.bonus_coins} бонус) — "
                f"{format_price(pack.price_rub)}"
            )
        else:
            lines.append(f"• {pack.coins} монеток — {format_price(pack.price_rub)}")
    
    lines.append("\n💡 Монетки не сгорают и доступны без активной подписки!")
    
    return "\n".join(lines)

def get_full_pricing_text() -> str:
    """Полный текст с ценами"""
    return "\n".join([
        format_tariffs_text(),
        format_feature_costs_text(),
        format_topup_packs_text(),
    ])

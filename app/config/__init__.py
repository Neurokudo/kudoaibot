"""
Конфигурация бота
"""
from .pricing import (
    TARIFFS,
    FEATURE_COSTS,
    TOPUP_PACKS,
    get_tariff_info,
    get_feature_cost,
    get_topup_pack,
    format_price
)

__all__ = [
    'TARIFFS',
    'FEATURE_COSTS',
    'TOPUP_PACKS',
    'get_tariff_info',
    'get_feature_cost',
    'get_topup_pack',
    'format_price'
]

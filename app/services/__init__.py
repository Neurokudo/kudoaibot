"""
Сервисы бота
"""
from .balance_manager import (
    get_balance,
    add_coins,
    spend_coins,
    can_afford
)
from .billing import (
    check_access,
    process_subscription_payment,
    process_topup_payment,
    deduct_coins_for_feature
)

__all__ = [
    'get_balance',
    'add_coins',
    'spend_coins',
    'can_afford',
    'check_access',
    'process_subscription_payment',
    'process_topup_payment',
    'deduct_coins_for_feature'
]

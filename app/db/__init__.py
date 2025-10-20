"""
Модуль для работы с базой данных
"""
from .database import (
    init_db,
    get_db_pool,
    close_db,
    execute_query,
    fetch_one,
    fetch_all
)
from .users import (
    create_user,
    get_user,
    update_user_balance,
    update_user_plan,
    get_user_balance
)
from .subscriptions import (
    create_subscription,
    get_active_subscription,
    deactivate_expired_subscriptions,
    check_subscription_status
)
from .transactions import (
    create_transaction,
    get_user_transactions,
    get_user_transaction_history
)

__all__ = [
    'init_db',
    'get_db_pool',
    'close_db',
    'execute_query',
    'fetch_one',
    'fetch_all',
    'create_user',
    'get_user',
    'update_user_balance',
    'update_user_plan',
    'get_user_balance',
    'create_subscription',
    'get_active_subscription',
    'deactivate_expired_subscriptions',
    'check_subscription_status',
    'create_transaction',
    'get_user_transactions',
    'get_user_transaction_history'
]

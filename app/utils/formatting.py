# app/utils/formatting.py
"""Утилиты форматирования текста"""

def pluralize_coins(count: int) -> str:
    """
    Склонение слова "монетка"
    
    Args:
        count: Количество монеток
    
    Returns:
        Правильная форма: монетка/монетки/монеток
    
    Examples:
        1 монетка
        2 монетки
        5 монеток
        21 монетка
    """
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} монетка"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return f"{count} монетки"
    else:
        return f"{count} монеток"

def format_coins(count: int, short: bool = False) -> str:
    """
    Форматировать количество монеток
    
    Args:
        count: Количество
        short: Короткий формат (монеток вместо склонения)
    
    Returns:
        Отформатированная строка
    """
    if short:
        return f"{count} монеток"
    else:
        return pluralize_coins(count)

def format_coins_per_second(coins: int) -> str:
    """Форматировать стоимость за секунду"""
    return f"{coins} {get_coin_word(coins)} за секунду"

def format_coins_per_operation(coins: int) -> str:
    """Форматировать стоимость за операцию"""
    return f"{coins} {get_coin_word(coins)} за операцию"

def get_coin_word(count: int) -> str:
    """
    Получить правильное склонение слова "монетка"
    
    Returns:
        монетка/монетки/монеток (без числа)
    """
    if count % 10 == 1 and count % 100 != 11:
        return "монетка"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "монетки"
    else:
        return "монеток"

# Константа для использования в UI
COIN_LABEL = "монетка"
COIN_LABEL_PLURAL = "монетки"
COIN_LABEL_MANY = "монеток"


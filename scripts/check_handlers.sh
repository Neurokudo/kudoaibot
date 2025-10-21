#!/bin/bash
# Быстрая проверка обработчиков

echo "🔍 Проверка обработчиков..."

# Извлекаем зарегистрированные функции
REGISTERED=$(grep -o "dp.callback_query.register(callback_[a-z_]*" app/handlers/callbacks.py | sed 's/dp.callback_query.register(//' | sort -u)

# Извлекаем определенные функции  
DEFINED=$(grep -o "^async def callback_[a-z_0-9]*" app/handlers/callbacks.py | sed 's/^async def //' | sort -u)

echo "Зарегистрировано: $(echo "$REGISTERED" | wc -l)"
echo "Определено: $(echo "$DEFINED" | wc -l)"

# Проверяем несоответствия
MISSING=$(comm -23 <(echo "$REGISTERED") <(echo "$DEFINED"))
UNUSED=$(comm -13 <(echo "$REGISTERED") <(echo "$DEFINED"))

if [ -n "$MISSING" ]; then
    echo "❌ ОШИБКА: Функции зарегистрированы, но не определены:"
    echo "$MISSING"
    exit 1
fi

if [ -n "$UNUSED" ]; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: Функции определены, но не зарегистрированы:"
    echo "$UNUSED"
fi

echo "✅ Все проверки пройдены!"

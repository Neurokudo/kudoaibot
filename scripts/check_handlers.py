#!/usr/bin/env python3
"""
Автоматическая проверка обработчиков перед коммитом
Проверяет соответствие между регистрацией и определением функций
"""

import os
import re
import sys
from pathlib import Path

def check_handlers():
    """Проверка обработчиков в callbacks.py"""
    callbacks_file = Path("app/handlers/callbacks.py")
    
    if not callbacks_file.exists():
        print("❌ Файл app/handlers/callbacks.py не найден")
        return False
    
    # Читаем файл
    with open(callbacks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Извлекаем все регистрируемые функции
    registered_pattern = r'dp\.callback_query\.register\(callback_([a-z_0-9]+)'
    registered_functions = set(re.findall(registered_pattern, content))
    
    # Извлекаем все определенные функции из всех файлов handlers
    defined_functions = set()
    handlers_dir = Path("app/handlers")
    
    for py_file in handlers_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        defined_pattern = r'^async def callback_([a-z_0-9]+)'
        file_functions = re.findall(defined_pattern, file_content, re.MULTILINE)
        defined_functions.update(file_functions)
    
    # Проверяем соответствие
    missing_definitions = registered_functions - defined_functions
    unused_definitions = defined_functions - registered_functions
    
    print("🔍 Проверка обработчиков:")
    print(f"   Зарегистрировано: {len(registered_functions)}")
    print(f"   Определено: {len(defined_functions)}")
    
    if missing_definitions:
        print(f"\n❌ ОШИБКА: Функции зарегистрированы, но не определены:")
        for func in sorted(missing_definitions):
            print(f"   - callback_{func}")
        return False
    
    if unused_definitions:
        print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЕ: Функции определены, но не зарегистрированы:")
        for func in sorted(unused_definitions):
            print(f"   - callback_{func}")
    
    print("\n✅ Все зарегистрированные функции имеют определения!")
    return True

def check_imports():
    """Проверка импортов в handlers/__init__.py"""
    init_file = Path("app/handlers/__init__.py")
    
    if not init_file.exists():
        print("❌ Файл app/handlers/__init__.py не найден")
        return False
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем импорты
    import_pattern = r'from \. import ([a-z_]+)'
    imports = re.findall(import_pattern, content)
    
    print(f"\n🔍 Проверка импортов:")
    print(f"   Импортировано модулей: {len(imports)}")
    
    # Проверяем существование модулей
    handlers_dir = Path("app/handlers")
    missing_modules = []
    
    for module in imports:
        module_file = handlers_dir / f"{module}.py"
        if not module_file.exists():
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ ОШИБКА: Импортируемые модули не найдены:")
        for module in missing_modules:
            print(f"   - {module}.py")
        return False
    
    print("✅ Все импортируемые модули существуют!")
    return True

def main():
    """Основная функция проверки"""
    print("🚀 Автоматическая проверка обработчиков...")
    
    # Переходим в корень проекта
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = True
    
    # Проверяем обработчики
    if not check_handlers():
        success = False
    
    # Проверяем импорты
    if not check_imports():
        success = False
    
    if success:
        print("\n🎉 Все проверки пройдены! Можно коммитить.")
        sys.exit(0)
    else:
        print("\n💥 Найдены ошибки! Исправьте их перед коммитом.")
        sys.exit(1)

if __name__ == "__main__":
    main()
